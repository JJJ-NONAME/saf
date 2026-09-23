import React from "react";
import { Project } from "../types/project";
import { icons } from "../utils/icons";
import { ProjectIcon, formatDate } from "./ProjectUtils";
import ContextMenu from "./ContextMenu";
import "../styles/ProjectsList.css";

export type ProjectsViewProps = {
  /** Array of projects to display */
  projects: Project[];
  /** Optional URL for the default project icon (solution-level override) */
  projectIconUrl?: string;
  /** Callback when edit button is clicked */
  onEdit: (project: Project) => void;
  /** Callback when delete button is clicked */
  onDelete: (projectId: string) => void;
  /** Callback when export button is clicked */
  onExport: (projectId: string) => void;
  /** Callback when a project card is clicked */
  onCardClick: (projectId: string) => void;
  /** Callback when favorite is toggled */
  onFavoriteToggle: (projectId: string) => void;
  /** Callback when info button is clicked */
  onInfo: (projectId: string) => void;
  /** Array of project IDs that are favorited */
  favoriteIds: string[];
};

/**
 * ProjectsList component displays a grid of project cards.
 * Each card shows project information and action buttons for Edit, Export, and Delete.
 */
const ProjectsList: React.FC<ProjectsViewProps> = ({
  projects,
  projectIconUrl,
  onEdit,
  onDelete,
  onExport,
  onCardClick,
  onFavoriteToggle,
  onInfo,
  favoriteIds,
}) => {
  if (projects.length === 0) {
    return (
      <div className="no-projects">
        <p>No projects found. Create your first project to get started!</p>
      </div>
    );
  }

  return (
    <div className="projects-list">
      <div className="projects-grid">
        {projects.map((project) => (
          // eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex
          <article
            key={project.name}
            className="project-card project-card-clickable"
            onClick={() => onCardClick(project.name)}
            tabIndex={0}
            aria-label={`Open project ${project.display_name}`}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                onCardClick(project.name);
              }
            }}
          >
            <div className="project-card-header">
              <ProjectIcon src={project.icon ?? projectIconUrl} />
              <div className="project-name-text">
                <h6>{project.display_name}</h6>
                <span className="projectid-label">
                  Id: {project.name.replace(/^projects\//, "")}
                </span>
              </div>

              <ContextMenu
                items={[
                  {
                    label: "Edit",
                    icon: icons.edit,
                    onClick: () => onEdit(project),
                  },
                  {
                    label: "Export",
                    icon: icons.download,
                    onClick: () => onExport(project.name),
                  },
                  {
                    label: "Delete",
                    icon: icons.delete,
                    onClick: () => onDelete(project.name),
                    className: "menu-item-danger",
                  },
                ]}
              />
            </div>
            <div className="project-card-body">
              <div className="project-info">
                <span className="info-label">Created:</span>
                <span className="info-label">Last Saved:</span>
              </div>
              <div className="project-info">
                <span className="info-value">
                  {formatDate(project.date_created)}
                </span>
                <span className="info-value">
                  {formatDate(project.date_modified)}
                </span>
              </div>
            </div>
            <div className="project-card-footer">
              <button
                className="btn-icon"
                onClick={(e) => {
                  e.stopPropagation();
                  onInfo(project.name);
                }}
                title="Project info"
                aria-label="Project info"
              >
                <span
                  className="awc-icon"
                  dangerouslySetInnerHTML={{ __html: icons.infoOutline }}
                />
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
};

export default ProjectsList;
