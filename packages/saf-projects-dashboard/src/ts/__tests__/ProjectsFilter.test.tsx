import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import ProjectsFilter from "../components/ProjectsFilter";
import { ProjectsFilters } from "../types/project";

describe("ProjectsFilter", () => {
  const baseValue: ProjectsFilters = {
    dateCreatedFrom: "2025-01-01",
    dateCreatedTo: "2025-12-31",
  };

  afterEach(() => {
    jest.useRealTimers();
  });

  it("renders search field and updates value when typing", () => {
    const onApply = jest.fn();
    const onClear = jest.fn();

    const { container } = render(
      <ProjectsFilter value={{}} onApply={onApply} onClear={onClear} />,
    );

    const input = screen.getByLabelText("Search projects") as HTMLInputElement;
    expect(input).toBeInTheDocument();
    expect(
      container.querySelector(".projects-search-prefix-icon"),
    ).toBeInTheDocument();

    fireEvent.change(input, { target: { value: "Motor" } });

    expect(input.value).toBe("Motor");
  });

  it("applies search after 300ms debounce and preserves other filters", () => {
    jest.useFakeTimers();

    const onApply = jest.fn();
    const onClear = jest.fn();

    render(
      <ProjectsFilter value={baseValue} onApply={onApply} onClear={onClear} />,
    );

    fireEvent.change(screen.getByLabelText("Search projects"), {
      target: { value: "Motor" },
    });

    act(() => {
      jest.advanceTimersByTime(299);
    });
    expect(onApply).not.toHaveBeenCalled();

    act(() => {
      jest.advanceTimersByTime(1);
    });

    expect(onApply).toHaveBeenCalledWith({
      search: "Motor",
      dateCreatedFrom: "2025-01-01",
      dateCreatedTo: "2025-12-31",
    });
  });

  it("clears only search and applies remaining filters", () => {
    const onApply = jest.fn();
    const onClear = jest.fn();

    render(
      <ProjectsFilter
        value={{
          search: "Rotor",
          dateCreatedFrom: "2025-01-01",
          dateCreatedTo: "2025-12-31",
        }}
        onApply={onApply}
        onClear={onClear}
      />,
    );

    fireEvent.click(screen.getByLabelText("Clear project search"));

    expect(onApply).toHaveBeenCalledWith({
      dateCreatedFrom: "2025-01-01",
      dateCreatedTo: "2025-12-31",
      search: undefined,
    });
    expect(onClear).not.toHaveBeenCalled();
  });
});
