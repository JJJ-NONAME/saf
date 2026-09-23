import React, { useState, useRef } from "react";
import { icons } from "../utils/icons";
import { validateProjectName } from "../utils/validation";
import "../styles/ImportExport.css";

type ImportExportProps = {
  /** Callback when import is requested with file content and display name */
  onImport: (
    fileContent: string,
    filename: string,
    displayName: string,
  ) => void;
};

/**
 * ImportExport component for importing projects from .safx files.
 *
 * This component provides a native React file upload experience:
 * - Click "Import Project" button to open a modal
 * - Drag & drop a .safx file or click to browse
 * - Enter a display name and click Import
 * - The `onImport` callback is triggered with the file data (base64)
 */
const ImportExport: React.FC<ImportExportProps> = ({ onImport }) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [displayName, setDisplayName] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [nameError, setNameError] = useState<string>("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Read file and convert to base64 data URL
   */
  const readFileAsBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = () => reject(new Error("Failed to read file"));
      reader.readAsDataURL(file);
    });
  };

  /**
   * Process selected file
   */
  const processFile = async (file: File) => {
    // Validate file extension
    if (!file.name.toLowerCase().endsWith(".safx")) {
      setError("Please select a .safx file");
      return;
    }

    setError("");
    setSelectedFile(file);

    // Auto-populate display name from filename
    const name = file.name.replace(/\.safx$/i, "");
    setDisplayName(name);

    // Read file content as base64
    try {
      const content = await readFileAsBase64(file);
      setFileContent(content);
    } catch {
      setError("Failed to read file");
      setSelectedFile(null);
    }
  };

  /**
   * Handle file input change
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  /**
   * Handle drag events
   */
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  /**
   * Open file browser
   */
  const handleBrowseClick = () => {
    fileInputRef.current?.click();
  };

  /**
   * Handle form submission
   */
  const handleImport = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!selectedFile || !fileContent) {
      setError("Please select a file");
      return;
    }

    if (!displayName.trim()) {
      setError("Please enter a project name");
      return;
    }

    const validationError = validateProjectName(displayName);
    if (validationError) {
      setNameError(validationError);
      return;
    }

    onImport(fileContent, selectedFile.name, displayName.trim());

    // Reset and close modal
    resetForm();
  };

  /**
   * Reset form state
   */
  const resetForm = () => {
    setShowModal(false);
    setDisplayName("");
    setSelectedFile(null);
    setFileContent("");
    setNameError("");
    setIsDragging(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  /**
   * Clear selected file
   */
  const handleClearFile = () => {
    setSelectedFile(null);
    setFileContent("");
    setDisplayName("");
    setError("");
    setNameError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="import-export-container">
      <button
        className="awc-btn awc-btn-secondary main-btn"
        onClick={() => setShowModal(true)}
      >
        <span
          className="awc-icon"
          dangerouslySetInnerHTML={{ __html: icons.import }}
        />
        Import Project
      </button>

      {/* Import Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={resetForm}>
          <div
            className="modal-content import-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>Import Project</h3>
            <form onSubmit={handleImport}>
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".safx"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />

              {/* Drag & Drop Zone */}
              <div className="form-group">
                <label>Project File (.safx) *</label>
                <div
                  className={`drop-zone ${isDragging ? "dragging" : ""} ${selectedFile ? "has-file" : ""}`}
                  onDragEnter={handleDragEnter}
                  onDragLeave={handleDragLeave}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={selectedFile ? undefined : handleBrowseClick}
                >
                  {selectedFile ? (
                    <div className="file-info">
                      <div className="file-icon">
                        <span
                          className="awc-icon"
                          dangerouslySetInnerHTML={{ __html: icons.document }}
                        />
                      </div>
                      <div className="file-details">
                        <strong>{selectedFile.name}</strong>
                        <span className="file-size">
                          {formatFileSize(selectedFile.size)}
                        </span>
                      </div>
                      <button
                        type="button"
                        className="btn-clear-file"
                        onClick={handleClearFile}
                        title="Remove file"
                      >
                        <span
                          className="awc-icon"
                          dangerouslySetInnerHTML={{ __html: icons.close }}
                        />
                      </button>
                    </div>
                  ) : (
                    <div className="drop-zone-content">
                      <div className="drop-icon">
                        <span
                          className="awc-icon"
                          dangerouslySetInnerHTML={{ __html: icons.folder }}
                        />
                      </div>
                      <div className="drop-text">
                        <strong>Drag & drop</strong> your .safx file here
                        <br />
                        or <span className="browse-link">browse</span> to select
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Project Name Input */}
              <div className="form-group">
                <label htmlFor="import-display-name">Project Name *</label>
                <input
                  type="text"
                  id="import-display-name"
                  value={displayName}
                  onChange={(e) => {
                    const value = e.target.value;
                    setDisplayName(value);
                    setNameError(validateProjectName(value));
                  }}
                  placeholder="Enter project name"
                  className={nameError ? "input-error" : ""}
                />
                {nameError && (
                  <span className="error-text">{nameError}</span>
                )}
              </div>

              {/* Error Message */}
              {error && <div className="import-error">{error}</div>}

              {/* Action Buttons */}
              <div className="modal-actions">
                <button
                  type="submit"
                  className="awc-btn awc-btn-primary"
                  disabled={!selectedFile || !displayName.trim() || !!nameError}
                >
                  Import
                </button>
                <button
                  type="button"
                  className="awc-btn awc-btn-secondary"
                  onClick={resetForm}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImportExport;
