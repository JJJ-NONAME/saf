import React from "react";
import { Project } from "../types/project";
import { formatDate } from "./ProjectUtils";
import { icons } from "../utils/icons";
import "../styles/ProjectInfo.css";

type ProjectInfoProps = {
  /** Project to show in the modal */
  project: Project;
  /** Called when the modal should close */
  onClose: () => void;
  /** Called when Open button is clicked */
  onOpen: () => void;
};

/**
 * ProjectInfo modal displays project metadata and actions.
 */
const ProjectInfo: React.FC<ProjectInfoProps> = ({
  project,
  onClose,
  onOpen,
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content modal-form"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="project-info-container">
          <div className="project-info-card">
            <button
              type="button"
              className="btn-icon project-info-close"
              onClick={onClose}
              aria-label="Close project information"
              title="Close"
            >
              <span
                className="awc-icon"
                dangerouslySetInnerHTML={{ __html: icons.close }}
              />
            </button>

            <h3>{project.display_name}</h3>

            <div className="project-info-row">
              <span className="info-label">Project ID:</span>
              <span className="info-value">{project.name}</span>
            </div>
            <div className="project-info-row">
              <span className="info-label">Created:</span>
              <span className="info-value">
                {formatDate(project.date_created)}
              </span>
            </div>
            <div className="project-info-row">
              <span className="info-label">Modified:</span>
              <span className="info-value">
                {formatDate(project.date_modified)}
              </span>
            </div>
            {/* Project description is optional, so only show if it exists */}
            {project.description && (
              <div className="project-info-row">
                <span className="info-label">Description:</span>
                <span className="info-value">{project.description}</span>
              </div>
            )}

            <div className="project-info-actions">
              <button
                type="button"
                className="awc-btn awc-btn-primary"
                onClick={onOpen}
              >
                Open
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectInfo;
