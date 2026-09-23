import React, { useEffect, useCallback, useMemo, useState } from "react";
import { DashComponentProps } from "../props";
import {
  Project,
  Notification,
  ActionResult,
  ProjectsFilters,
} from "../types/project";
import {
  createProjectsApi,
  ProjectsApiClient,
  ApiError,
} from "../api/projectsApi";
import { icons } from "../utils/icons";
import { useTheme } from "../hooks/useTheme";
import ProjectsList from "./ProjectsList";
import ProjectsTable from "./ProjectsTable";
import ProjectForm from "./ProjectForm";
import ProjectInfo from "./ProjectInfo";
import ImportExport from "./ImportExport";
import SolutionMetadata from "./SolutionMetadata";
import Pagination, { DEFAULT_PAGE_SIZE } from "./Pagination";
import ProjectsFilter from "./ProjectsFilter";

// AWC Design System: tokens and fonts (must be imported before component styles)
import "../assets/default.css";
import "../styles/fonts.css";
import "../styles/Dashboard.css";

/**
 * ProjectsDashboard is a Dash component that provides a complete CRUD interface
 * for managing GLOW projects. It includes project listing, creation, editing,
 * deletion, import, and export functionality.
 *
 * All state is exposed via props for Python callback integration. Use dcc.Upload
 * component to handle file uploads and pass the uploaded file data to this component.
 */
type Props = {
  /**
   * Base URL for the GLOW API backend.
   * If provided, API calls will use this URL (e.g., "http://127.0.0.1:5678").
   * If not provided, uses relative URLs which require a Flask proxy to forward requests.
   */
  apiBaseUrl?: string;

  /**
   * URL for the default project icon displayed on project cards.
   * If provided, this URL is used as the `<img src>` for every card that
   * does not supply its own per-project `icon` field.
   * If omitted, a bundled inline SVG icon is rendered instead (zero HTTP requests).
   */
  projectIconUrl?: string;

  /**
   * URL for the solution application image displayed in the header.
   * Typically points to a Dash-served asset (e.g., "/assets/application.svg").
   * If omitted or fails to load, a bundled inline SVG is rendered instead.
   */
  solutionImageUrl?: string;

  /**
   * Description text for the solution displayed in the header.
   * If omitted, defaults to "Here is the description of the solution..."
   */
  solutionDescription?: string;

  /**
   * List of projects currently loaded.
   * Updated automatically when projects are loaded, created, updated, or deleted.
   */
  projects?: Project[];

  /**
   * Whether the component is currently loading data.
   */
  loading?: boolean;

  /**
   * Current error message, if any.
   */
  error?: string | null;

  /**
   * Currently selected project for editing.
   * Set when user clicks Edit on a project card.
   */
  selectedProject?: Project | null;

  /**
   * Whether the create project form is currently shown.
   */
  showCreateForm?: boolean;

  /**
   * Current notification message to display.
   */
  notification?: Notification | null;

  /**
   * Result of the last action performed (for callback tracking).
   * Updated after each CRUD operation completes.
   */
  actionResult?: ActionResult | null;

  /**
   * ID of project pending deletion (for confirmation modal).
   */
  pendingDeleteId?: string | null;

  /**
   * Whether to show the upgrade snackbar.
   */
  showUpgradeSnackbar?: boolean;

  /**
   * ID of project pending upgrade.
   */
  upgradeProjectId?: string | null;

  /**
   * Theme Mode for the dashboard: "light" or "dark".
   * When provided externally (e.g., from DMC MantineProvider), the component
   * uses this value and hides its own theme toggle button.
   */
  themeMode?: "light" | "dark";

  /**
   * 1-based index of the currently displayed page. Defaults to 1.
   */
  currentPage?: number;

  /**
   * Number of projects displayed per page. Defaults to 10.
   * Allowed values surfaced in the UI: 5, 10, 20, 50.
   */
  pageSize?: number;

  /**
   * Total number of projects available on the server. Set automatically
   * after each project load so Python callbacks can read it.
   */
  totalProjects?: number;

  /**
   * Total number of pages available on the server for the current `pageSize`.
   * Set automatically after each project load so Python callbacks can read it.
   */
  totalPages?: number;

  /**
   * Applied date-range filters forwarded to GLOW `GET /projects`.
   * Updated when the user clicks Apply or Clear all in the filter bar.
   */
  filters?: ProjectsFilters;
} & DashComponentProps;

/**
 * ProjectsDashboard - A Dash component for managing GLOW projects.
 *
 * This component provides a complete CRUD interface for GLOW projects:
 * - List all projects in a card grid
 * - Create new projects
 * - Edit existing project names
 * - Delete projects (with confirmation)
 * - Export projects as .safx files
 * - Import projects from .safx files (via dcc.Upload integration)
 *
 * All state is exposed as props for Python callback integration:
 * - `projects`: Current list of projects
 * - `loading`: Loading state
 * - `error`: Error messages
 * - `actionResult`: Result of last CRUD operation
 * - `notification`: User-facing notifications
 *
 * Example usage in Python:
 * ```python
 * import ansys_saf_projects_dashboard
 * from dash import callback, Input, Output
 *
 * app.layout = html.Div([
 *     ansys_saf_projects_dashboard.ProjectsDashboard(id='dashboard'),
 * ])
 *
 * @callback(
 *     Output('output', 'children'),
 *     Input('dashboard', 'actionResult'),
 * )
 * def handle_action(action_result):
 *     if action_result:
 *         return f"Action: {action_result['action']}, Success: {action_result['success']}"
 *     return ""
 * ```
 */
const ProjectsDashboard: React.FC<Props> = (props) => {
  const {
    id,
    setProps,
    apiBaseUrl,
    projectIconUrl,
    solutionImageUrl,
    solutionDescription,
    projects: propProjects,
    loading: propLoading,
    error: propError,
    selectedProject: propSelectedProject,
    showCreateForm: propShowCreateForm,
    notification: propNotification,
    pendingDeleteId: propPendingDeleteId,
    showUpgradeSnackbar: propShowUpgradeSnackbar,
    upgradeProjectId: propUpgradeProjectId,
    themeMode: propTheme,
    currentPage: propCurrentPage,
    pageSize: propPageSize,
    totalProjects: propTotalProjects,
    totalPages: propTotalPages,
    filters: propFilters,
  } = props;

  // Create a memoized API client configured with the baseUrl
  // This ensures all API calls use the correct backend URL
  const api: ProjectsApiClient = useMemo(
    () => createProjectsApi(apiBaseUrl),
    [apiBaseUrl],
  );

  // Use prop values or defaults for controlled state
  const projects = propProjects ?? [];
  const loading = propLoading ?? true;
  const error = propError ?? null;
  const selectedProject = propSelectedProject ?? null;
  const showCreateForm = propShowCreateForm ?? false;
  const notification = propNotification ?? null;
  const pendingDeleteId = propPendingDeleteId ?? null;
  const showUpgradeSnackbar = propShowUpgradeSnackbar ?? false;
  const upgradeProjectId = propUpgradeProjectId ?? null;
  const currentPage = propCurrentPage ?? 1;
  const pageSize = propPageSize ?? DEFAULT_PAGE_SIZE;
  const totalProjects = propTotalProjects ?? 0;
  const totalPages = propTotalPages ?? 1;
  const filters = useMemo(() => propFilters ?? {}, [propFilters]);

  // Local favorite state (not persisted to API)
  const [favoriteIds, setFavoriteIds] = useState<string[]>([]);

  // Local view mode state: "grid" (cards) or "table" (list rows)
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

  // Local state for the project info modal
  const [infoProject, setInfoProject] = useState<Project | null>(null);

  // Theme management: use external prop if provided, otherwise system preference → localStorage → "light"
  const { themeMode, toggleTheme } = useTheme(propTheme);

  // Load projects whenever pagination, filters, or the API base change
  useEffect(() => {
    loadProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiBaseUrl, currentPage, pageSize, filters]);

  // Auto-clear notification after 5 seconds
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => {
        setProps({ notification: null });
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  /**
   * Show a notification message to the user.
   */
  const showNotification = useCallback(
    (message: string, type: Notification["type"]) => {
      setProps({ notification: { message, type } });
    },
    [setProps],
  );

  /**
   * Emit an action result for Python callback tracking.
   */
  const emitActionResult = useCallback(
    (
      action: ActionResult["action"],
      success: boolean,
      projectId?: string,
      message?: string,
    ) => {
      const result: ActionResult = {
        action,
        success,
        projectId,
        message,
        timestamp: Date.now(),
      };
      setProps({ actionResult: result });
    },
    [setProps],
  );

  /**
   * Load projects from the API for the current page.
   */
  const loadProjects = async () => {
    try {
      setProps({ loading: true, error: null });
      const data = await api.listProjects(currentPage, pageSize, filters);
      setProps({
        projects: data.projects,
        totalProjects: data.total_projects,
        totalPages: data.total_pages,
        loading: false,
      });
      emitActionResult(
        "list",
        true,
        undefined,
        `Loaded ${data.projects.length} of ${data.total_projects} projects`,
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setProps({
        error: `Failed to load projects: ${message}`,
        loading: false,
        projects: [],
        totalProjects: 0,
        totalPages: 1,
      });
      emitActionResult("list", false, undefined, message);
    }
  };

  const handlePageChange = useCallback(
    (page: number) => {
      setProps({ currentPage: page });
    },
    [setProps],
  );

  const handlePageSizeChange = useCallback(
    (size: number) => {
      setProps({ pageSize: size, currentPage: 1 });
    },
    [setProps],
  );

  const handleFilterApply = useCallback(
    (nextFilters: ProjectsFilters) => {
      setProps({ filters: nextFilters, currentPage: 1 });
    },
    [setProps],
  );

  const handleFilterClear = useCallback(() => {
    setProps({ filters: {}, currentPage: 1 });
  }, [setProps]);

  /**
   * Handle creating a new project.
   */
  const handleCreateProject = async (
    displayName: string,
    description?: string,
  ) => {
    try {
      const newProject = await api.createProject(displayName, description);
      setProps({ showCreateForm: false });
      showNotification("Project created successfully", "success");
      emitActionResult("create", true, newProject.name, displayName);
      await loadProjects();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to create project: ${message}`, "error");
      emitActionResult("create", false, undefined, message);
    }
  };

  /**
   * Handle updating an existing project.
   */
  const handleUpdateProject = async (
    projectId: string,
    displayName: string,
    description?: string,
  ) => {
    try {
      const updatedProject = await api.updateProject(
        projectId,
        displayName,
        description,
      );
      setProps({
        projects: projects.map((p) =>
          p.name === projectId ? updatedProject : p,
        ),
        selectedProject: null,
      });
      showNotification("Project updated successfully", "success");
      emitActionResult("update", true, projectId, displayName);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to update project: ${message}`, "error");
      emitActionResult("update", false, projectId, message);
    }
  };

  /**
   * Handle delete button click - show confirmation modal.
   */
  const handleDeleteClick = (projectId: string) => {
    setProps({ pendingDeleteId: projectId });
  };

  /**
   * Handle delete confirmation.
   */
  const handleConfirmDelete = async () => {
    if (!pendingDeleteId) return;

    try {
      await api.deleteProject(pendingDeleteId);
      setProps({ pendingDeleteId: null });
      showNotification("Project deleted successfully", "success");
      emitActionResult("delete", true, pendingDeleteId);
      await loadProjects();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to delete project: ${message}`, "error");
      emitActionResult("delete", false, pendingDeleteId, message);
      setProps({ pendingDeleteId: null });
    }
  };

  /**
   * Handle delete cancellation.
   */
  const handleCancelDelete = () => {
    setProps({ pendingDeleteId: null });
  };

  /**
   * Handle exporting a project.
   */
  const handleExportProject = async (projectId: string) => {
    try {
      const blob = await api.exportProject(projectId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      // Extract project name from full path (e.g., "projects/abc123" -> "abc123")
      const filename = projectId.replace("projects/", "");
      a.download = `${filename}.safx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showNotification("Project exported successfully", "success");
      emitActionResult("export", true, projectId);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to export project: ${message}`, "error");
      emitActionResult("export", false, projectId, message);
    }
  };

  /**
   * Navigate to project URL.
   */
  const navigateToProject = (projectName: string) => {
    const origin = globalThis.location.origin;
    const newUrl = `${origin}/${projectName}`;
    globalThis.open(newUrl, "_self");
  };

  /**
   * Handle clicking on a project card.
   * Calls getProject API and handles 422 error for upgrade flow.
   */
  const handleCardClick = async (projectId: string) => {
    try {
      const project = await api.getProject(projectId);
      navigateToProject(project.name);
    } catch (err) {
      // Check if it's a 422 error (requires upgrade)
      if (err.status === 422) {
        setProps({
          showUpgradeSnackbar: true,
          upgradeProjectId: projectId,
        });
      } else {
        const message = err instanceof Error ? err.message : "Unknown error";
        showNotification(`Failed to open project: ${message}`, "error");
      }
    }
  };

  /**
   * Handle upgrade button click in snackbar.
   */
  const handleUpgrade = async () => {
    if (!upgradeProjectId) return;

    try {
      const project = await api.upgradeProject(upgradeProjectId);
      setProps({
        showUpgradeSnackbar: false,
        upgradeProjectId: null,
      });
      showNotification("Project upgraded successfully", "success");
      emitActionResult(
        "upgrade",
        true,
        upgradeProjectId,
        "Project upgraded successfully",
      );
      navigateToProject(project.name);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to upgrade project: ${message}`, "error");
      emitActionResult("upgrade", false, upgradeProjectId, message);
      setProps({
        showUpgradeSnackbar: false,
        upgradeProjectId: null,
      });
    }
  };

  /**
   * Handle dismiss upgrade snackbar.
   */
  const handleDismissUpgrade = () => {
    setProps({
      showUpgradeSnackbar: false,
      upgradeProjectId: null,
    });
  };

  /**
   * Handle importing a project from file upload.
   */
  const handleImportProject = async (
    fileContent: string,
    filename: string,
    displayName: string,
  ) => {
    try {
      const newProject = await api.importProject(
        fileContent,
        filename,
        displayName,
      );
      showNotification("Project imported successfully", "success");
      emitActionResult("import", true, newProject.name, displayName);
      await loadProjects();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      showNotification(`Failed to import project: ${message}`, "error");
      emitActionResult("import", false, undefined, message);
    }
  };

  /**
   * Toggle the create form visibility.
   */
  const handleToggleCreateForm = () => {
    setProps({ showCreateForm: !showCreateForm });
  };

  /**
   * Handle edit button click.
   */
  const handleEditClick = (project: Project) => {
    setProps({ selectedProject: project });
  };

  /**
   * Toggle favorite state for a project.
   */
  const handleFavoriteToggle = (projectId: string) => {
    setFavoriteIds((prev) =>
      prev.includes(projectId)
        ? prev.filter((id) => id !== projectId)
        : [...prev, projectId],
    );
  };

  /**
   * Handle info button click.
   */
  const handleInfo = (projectId: string) => {
    const project = projects.find((p) => p.name === projectId);
    if (project) {
      setInfoProject(project);
    }
  };

  /**
   * Handle closing the project info modal.
   */
  const handleCloseInfo = () => {
    setInfoProject(null);
  };

  /**
   * Handle opening the selected project from the info modal.
   */
  const handleOpenFromInfo = () => {
    if (!infoProject) return;
    navigateToProject(infoProject.name);
  };

  /**
   * Handle edit form cancel.
   */
  const handleCancelEdit = () => {
    setProps({ selectedProject: null });
  };

  /**
   * Handle create form cancel.
   */
  const handleCancelCreate = () => {
    setProps({ showCreateForm: false });
  };

  /**
   * Handle opening the documentation from the help icon.
   * redirects to the documentation page in same tab.
   */
  const handleOpenDocumentation = () => {
    const originUrl = globalThis.location.origin;
    globalThis.open(`${originUrl}/documentation/index.html`, "_self");
  };

  return (
    <div id={id} className="dashboard-container">
      <div className="dashboard-topbar">
        <button
          className="awc-btn-tertiary main-btn"
          onClick={loadProjects}
          disabled={loading}
        >
          <span
            className="awc-icon"
            dangerouslySetInnerHTML={{ __html: icons.restart }}
          />
          Refresh
        </button>
        <ImportExport onImport={handleImportProject} />
        <button
          className="awc-btn awc-btn-primary main-btn"
          onClick={handleToggleCreateForm}
        >
          {showCreateForm ? (
            "Cancel"
          ) : (
            <>
              <span
                className="awc-icon"
                dangerouslySetInnerHTML={{ __html: icons.addGeometry }}
              />{" "}
              New Project
            </>
          )}
        </button>
        <button
          className="btn-icon theme-toggle-btn"
          onClick={handleOpenDocumentation}
          title={"Documentation"}
          aria-label={"documentation help"}
        >
          <span
            className="awc-icon"
            dangerouslySetInnerHTML={{
              __html: icons.help,
            }}
          />
        </button>
      </div>
      <SolutionMetadata
        solutionImageUrl={solutionImageUrl}
        solutionDescription={solutionDescription}
      />
      <div className="dashboard-header">
        <h4>Projects Dashboard</h4>
        {!propTheme && (
          <button
            className="btn-icon theme-toggle-btn"
            onClick={toggleTheme}
            title={
              themeMode === "light"
                ? "Switch to dark theme"
                : "Switch to light theme"
            }
            aria-label={
              themeMode === "light"
                ? "Switch to dark theme"
                : "Switch to light theme"
            }
          >
            <span
              className="awc-icon"
              dangerouslySetInnerHTML={{
                __html: themeMode === "light" ? icons.moon : icons.sun,
              }}
            />
          </button>
        )}
      </div>

      {notification && (
        <div className={`notification notification-${notification.type}`}>
          <span
            className="awc-icon"
            dangerouslySetInnerHTML={{
              __html:
                notification.type === "success"
                  ? icons.check
                  : notification.type === "error"
                    ? icons.error
                    : notification.type === "warning"
                      ? icons.warning
                      : icons.infoOutline,
            }}
          />
          {notification.message}
        </div>
      )}

      <div className="dashboard-actions">
        <ProjectsFilter
          value={filters}
          onApply={handleFilterApply}
          onClear={handleFilterClear}
        />
        <div className="align-right">
          <div className="view-toggle">
            <button
              className={`btn-icon ${viewMode === "grid" ? "btn-icon-active" : ""}`}
              onClick={() => setViewMode("grid")}
              title="Grid view"
              aria-label="Grid view"
              aria-pressed={viewMode === "grid"}
            >
              <span
                className="awc-icon"
                dangerouslySetInnerHTML={{ __html: icons.viewBlocks }}
              />
            </button>
            <button
              className={`btn-icon ${viewMode === "table" ? "btn-icon-active" : ""}`}
              onClick={() => setViewMode("table")}
              title="Table view"
              aria-label="Table view"
              aria-pressed={viewMode === "table"}
            >
              <span
                className="awc-icon"
                dangerouslySetInnerHTML={{ __html: icons.viewList }}
              />
            </button>
          </div>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading projects...</div>
      ) : viewMode === "grid" ? (
        <ProjectsList
          projects={projects}
          projectIconUrl={projectIconUrl}
          onEdit={handleEditClick}
          onDelete={handleDeleteClick}
          onExport={handleExportProject}
          onCardClick={handleCardClick}
          onFavoriteToggle={handleFavoriteToggle}
          onInfo={handleInfo}
          favoriteIds={favoriteIds}
        />
      ) : (
        <ProjectsTable
          projects={projects}
          projectIconUrl={projectIconUrl}
          onEdit={handleEditClick}
          onDelete={handleDeleteClick}
          onExport={handleExportProject}
          onCardClick={handleCardClick}
          onFavoriteToggle={handleFavoriteToggle}
          onInfo={handleInfo}
          favoriteIds={favoriteIds}
        />
      )}

      {!loading && totalProjects > 0 && (
        <Pagination
          currentPage={currentPage}
          pageSize={pageSize}
          totalProjects={totalProjects}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
        />
      )}

      {/* Create project modal */}
      {showCreateForm && (
        <div className="modal-overlay" onClick={handleCancelCreate}>
          <div
            className="modal-content modal-form"
            onClick={(e) => e.stopPropagation()}
          >
            <ProjectForm
              onSubmit={handleCreateProject}
              onCancel={handleCancelCreate}
            />
          </div>
        </div>
      )}

      {/* Edit project modal */}
      {selectedProject && (
        <div className="modal-overlay" onClick={handleCancelEdit}>
          <div
            className="modal-content modal-form"
            onClick={(e) => e.stopPropagation()}
          >
            <ProjectForm
              project={selectedProject}
              onSubmit={(displayName, description) =>
                handleUpdateProject(
                  selectedProject.name,
                  displayName,
                  description,
                )
              }
              onCancel={handleCancelEdit}
            />
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {pendingDeleteId && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Confirm Delete</h3>
            <p>
              Are you sure you want to delete this project? This action cannot
              be undone.
            </p>
            <div className="modal-actions">
              <button
                className="awc-btn awc-btn-delete"
                onClick={handleConfirmDelete}
              >
                Delete
              </button>
              <button
                className="awc-btn awc-btn-secondary"
                onClick={handleCancelDelete}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upgrade confirmation modal */}
      {showUpgradeSnackbar && (
        <div className="modal-overlay" onClick={handleDismissUpgrade}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Upgrade Required</h3>
            <p>
              By accepting an auto-upgrade you consent that some previous data
              might be lost.
            </p>
            <div className="modal-actions">
              <button
                className="awc-btn awc-btn-primary"
                onClick={handleUpgrade}
              >
                Upgrade
              </button>
              <button
                className="awc-btn awc-btn-secondary"
                onClick={handleDismissUpgrade}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Project info modal */}
      {infoProject && (
        <ProjectInfo
          project={infoProject}
          onClose={handleCloseInfo}
          onOpen={handleOpenFromInfo}
        />
      )}
    </div>
  );
};

export default ProjectsDashboard;
