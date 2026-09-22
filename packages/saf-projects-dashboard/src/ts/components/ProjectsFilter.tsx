import React, { useEffect, useRef, useState } from "react";
import { ProjectsFilters } from "../types/project";
import "../styles/ProjectsFilter.css";
import { icons } from "../utils/icons";

export type ProjectsFilterProps = {
  value: ProjectsFilters;
  onApply: (filters: ProjectsFilters) => void;
  onClear: () => void;
};

type OpenPopover = "created" | "modified" | null;

function filtersEqual(a: ProjectsFilters, b: ProjectsFilters): boolean {
  return (
    a.search === b.search &&
    a.dateCreatedFrom === b.dateCreatedFrom &&
    a.dateCreatedTo === b.dateCreatedTo &&
    a.dateModifiedFrom === b.dateModifiedFrom &&
    a.dateModifiedTo === b.dateModifiedTo
  );
}

function normalizeFilters(filters: ProjectsFilters): ProjectsFilters {
  const search = filters.search?.trim();
  return {
    ...filters,
    search: search || undefined,
  };
}

function isRangeInvalid(from?: string, to?: string): boolean {
  if (!from || !to) return false;
  return to < from;
}

function formatRangeLabel(
  from: string | undefined,
  to: string | undefined,
  placeholder: string,
): string {
  if (from && to) return `${from} → ${to}`;
  if (from) return `${from} → …`;
  if (to) return `… → ${to}`;
  return placeholder;
}

type DateRangeFieldProps = {
  id: string;
  label: string;
  placeholder: string;
  from?: string;
  to?: string;
  open: boolean;
  onToggle: () => void;
  onFromChange: (value: string) => void;
  onToChange: (value: string) => void;
};

type SearchInputFieldProps = {
  id: string;
  label: string;
  placeholder: string;
  prefixIcon?: string;
  clearIcon?: string;
  searchValue?: string;
  onChange: (value: string) => void;
  onClear: () => void;
};

const SearchInputField: React.FC<SearchInputFieldProps> = ({
  id,
  label,
  placeholder,
  prefixIcon,
  clearIcon,
  searchValue: value,
  onChange,
  onClear,
}) => {
  const searchValue = value ?? "";
  const hasValue = searchValue.length > 0;

  return (
    <div className="projects-filter-field projects-filter-search-field">
      <span
        className="projects-search-prefix-icon"
        aria-hidden="true"
        dangerouslySetInnerHTML={{ __html: prefixIcon || icons.search }}
      />
      <input
        tabIndex={0}
        id={`${id}-search`}
        name={`${id}-search`}
        type="text"
        className="awc-input search projects-search-filter"
        value={searchValue}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={label}
      />
      <button
        type="button"
        className="awc-btn awc-btn-tertiary projects-filter-clear-btn"
        aria-label="Clear project search"
        onClick={onClear}
        disabled={!hasValue}
      >
        <span
          className="awc-icon"
          dangerouslySetInnerHTML={{ __html: clearIcon || icons.close }}
        />
      </button>
    </div>
  );
};

const DateRangeField: React.FC<DateRangeFieldProps> = ({
  id,
  label,
  placeholder,
  from,
  to,
  open,
  onToggle,
  onFromChange,
  onToChange,
}) => {
  const popoverRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const handleMouseDown = (event: MouseEvent) => {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(event.target as Node)
      ) {
        onToggle();
      }
    };
    document.addEventListener("mousedown", handleMouseDown);
    return () => document.removeEventListener("mousedown", handleMouseDown);
  }, [open, onToggle]);

  const triggerLabel = formatRangeLabel(from, to, placeholder);
  const invalid = isRangeInvalid(from, to);

  return (
    <div className="projects-filter-field" ref={popoverRef}>
      <button
        type="button"
        id={`${id}-trigger`}
        className="awc-btn awc-btn-secondary projects-filter-trigger"
        onClick={onToggle}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-controls={`${id}-popover`}
        aria-label={label}
      >
        {triggerLabel} ▾
      </button>
      {open && (
        <div
          id={`${id}-popover`}
          className="projects-filter-popover"
          role="dialog"
          aria-label={label}
        >
          <label className="projects-filter-date-label" htmlFor={`${id}-from`}>
            Start
          </label>
          <input
            id={`${id}-from`}
            type="date"
            className="projects-filter-date-input"
            value={from ?? ""}
            onChange={(event) => onFromChange(event.target.value)}
          />
          <label className="projects-filter-date-label" htmlFor={`${id}-to`}>
            End
          </label>
          <input
            id={`${id}-to`}
            type="date"
            className="projects-filter-date-input"
            value={to ?? ""}
            onChange={(event) => onToChange(event.target.value)}
          />
          {invalid && (
            <p className="projects-filter-range-warning" role="alert">
              End date must be on or after start date.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

const ProjectsFilter: React.FC<ProjectsFilterProps> = ({
  value,
  onApply,
  onClear,
}) => {
  const [draft, setDraft] = useState<ProjectsFilters>(value);
  const [openPopover, setOpenPopover] = useState<OpenPopover>(null);
  const skipNextDebounceRef = useRef(false);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  useEffect(() => {
    if (skipNextDebounceRef.current) {
      skipNextDebounceRef.current = false;
      return;
    }

    const nextSearch = draft.search?.trim() || "";
    const appliedSearch = value.search?.trim() || "";
    if (nextSearch === appliedSearch) return;

    const timeoutId = window.setTimeout(() => {
      if (isRangeInvalid(draft.dateCreatedFrom, draft.dateCreatedTo)) return;
      if (isRangeInvalid(draft.dateModifiedFrom, draft.dateModifiedTo)) return;
      setOpenPopover(null);
      onApply(normalizeFilters(draft));
    }, 300);

    return () => window.clearTimeout(timeoutId);
  }, [
    draft,
    onApply,
    value.search,
    value.dateCreatedFrom,
    value.dateCreatedTo,
    value.dateModifiedFrom,
    value.dateModifiedTo,
  ]);

  const createdInvalid = isRangeInvalid(
    draft.dateCreatedFrom,
    draft.dateCreatedTo,
  );
  const modifiedInvalid = isRangeInvalid(
    draft.dateModifiedFrom,
    draft.dateModifiedTo,
  );
  const hasValidationError = createdInvalid || modifiedInvalid;
  const applyDisabled = filtersEqual(draft, value) || hasValidationError;

  const updateDraft = (patch: Partial<ProjectsFilters>) => {
    setDraft((prev) => ({ ...prev, ...patch }));
  };

  const togglePopover = (target: OpenPopover) => {
    setOpenPopover((current) => (current === target ? null : target));
  };

  const handleApply = () => {
    if (applyDisabled) return;
    setOpenPopover(null);
    onApply(normalizeFilters(draft));
  };

  const handleClear = () => {
    skipNextDebounceRef.current = true;
    setDraft({});
    setOpenPopover(null);
    onClear();
  };

  const handleSearchClear = () => {
    const nextDraft = normalizeFilters({ ...draft, search: undefined });
    skipNextDebounceRef.current = true;
    setDraft(nextDraft);
    setOpenPopover(null);
    onApply(nextDraft);
  };

  // TODO: This is a temporary placeholder until we implement the full filter expand and minimize  UI
  const clickFilters = () => {};

  return (
    <div className="projects-filter" aria-label="Project filters">
      <div className="projects-filter-fields">
        <button className="awc-btn-tertiary main-btn" onClick={clickFilters}>
          <span
            className="awc-icon"
            dangerouslySetInnerHTML={{ __html: icons.filter }}
          />
          Filters
        </button>
        <SearchInputField
          id="projects-search"
          label="Search projects"
          placeholder="Search..."
          prefixIcon={icons.search}
          clearIcon={icons.close}
          searchValue={draft.search}
          onChange={(value: string) =>
            updateDraft({ search: value || undefined })
          }
          onClear={handleSearchClear}
        />
        <DateRangeField
          id="projects-filter-created"
          label="Projects created date range"
          placeholder="Projects created"
          from={draft.dateCreatedFrom}
          to={draft.dateCreatedTo}
          open={openPopover === "created"}
          onToggle={() => togglePopover("created")}
          onFromChange={(next) =>
            updateDraft({ dateCreatedFrom: next || undefined })
          }
          onToChange={(next) =>
            updateDraft({ dateCreatedTo: next || undefined })
          }
        />
        <DateRangeField
          id="projects-filter-modified"
          label="Projects modified date range"
          placeholder="Projects modified"
          from={draft.dateModifiedFrom}
          to={draft.dateModifiedTo}
          open={openPopover === "modified"}
          onToggle={() => togglePopover("modified")}
          onFromChange={(next) =>
            updateDraft({ dateModifiedFrom: next || undefined })
          }
          onToChange={(next) =>
            updateDraft({ dateModifiedTo: next || undefined })
          }
        />
      </div>
      <div className="projects-filter-actions">
        <button
          type="button"
          className="awc-btn awc-btn-primary"
          onClick={handleApply}
          disabled={applyDisabled}
        >
          Apply
        </button>
        <button
          type="button"
          className="awc-btn awc-btn-secondary"
          onClick={handleClear}
        >
          Clear all
        </button>
      </div>
    </div>
  );
};

export default ProjectsFilter;
