import React, { useState, useEffect } from "react";
import { Project } from "../types/project";
import { validateProjectName } from "../utils/validation";
import "../styles/ProjectForm.css";

type ProjectFormProps = {
  /** Existing project for editing (undefined for create mode) */
  project?: Project;
  /** Callback when form is submitted with the display name and description */
  onSubmit: (displayName: string, description: string) => void;
  /** Callback when cancel button is clicked */
  onCancel: () => void;
};

/**
 * ProjectForm component for creating or editing projects.
 * Shows a form with project name input and submit/cancel buttons.
 */
const ProjectForm: React.FC<ProjectFormProps> = ({
  project,
  onSubmit,
  onCancel,
}) => {
  const [displayName, setDisplayName] = useState<string>(
    project?.display_name || "",
  );
  const [description, setDescription] = useState<string>(
    project?.description || "",
  );
  const [error, setError] = useState<string>("");

  // Update displayName and description when project prop changes (for edit mode)
  useEffect(() => {
    if (project?.display_name) {
      setDisplayName(project.display_name);
    }
    if (project?.description !== undefined) {
      setDescription(project.description);
    }
  }, [project]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!displayName.trim()) {
      setError("Project name is required");
      return;
    }

    const nameError = validateProjectName(displayName);
    if (nameError) {
      setError(nameError);
      return;
    }

    onSubmit(displayName.trim(), description.trim());
    setDisplayName("");
    setDescription("");
    setError("");
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setDisplayName(value);
    const nameError = validateProjectName(value);
    setError(nameError);
  };

  const handleDescriptionChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>,
  ) => {
    const text = e.target.value;
    const wordCount = text
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0).length;

    // Prevent exceeding 200 words
    if (wordCount <= 200) {
      setDescription(text);
      setError("");
    }
  };

  const getWordCount = (): number => {
    return description
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0).length;
  };

  return (
    <div className="project-form-container">
      <div className="project-form-card">
        <h3>{project ? "Edit Project" : "Create New Project"}</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="displayName">Project Name *</label>
            <input
              type="text"
              id="displayName"
              value={displayName}
              onChange={handleInputChange}
              placeholder="Enter project name"
              className={error ? "input-error" : ""}
              autoFocus
            />
            <label htmlFor="description">Project Description</label>
            <textarea
              id="description"
              value={description}
              onChange={handleDescriptionChange}
              placeholder="Enter project description"
              className={error ? "input-error" : ""}
              rows={3}
            />
            {error && <span className="error-text">{error}</span>}
          </div>

          {project && (
            <div className="form-info">
              <span className="info-label">Project ID:</span>
              <span className="info-value">{project.name}</span>
            </div>
          )}

          <div className="form-actions">
            <button type="submit" className="awc-btn awc-btn-primary">
              {project ? "Update" : "Create"}
            </button>
            <button
              type="button"
              className="awc-btn awc-btn-secondary"
              onClick={onCancel}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProjectForm;
