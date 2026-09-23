/**
 * Tests for ImportExport component
 */
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ImportExport from "../components/ImportExport";

describe("ImportExport", () => {
  const mockOnImport = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders import button initially", () => {
    render(<ImportExport onImport={mockOnImport} />);

    expect(
      screen.getByRole("button", { name: /import project/i }),
    ).toBeInTheDocument();
  });

  it("shows import modal when button is clicked", () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    expect(
      screen.getByRole("heading", { level: 3, name: /import project/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/Project Name/i)).toBeInTheDocument();
    expect(screen.getByText(/Drag & drop/i)).toBeInTheDocument();
  });

  it("hides modal when cancel is clicked", () => {
    render(<ImportExport onImport={mockOnImport} />);

    // Open modal
    fireEvent.click(screen.getByRole("button", { name: /import project/i }));
    expect(
      screen.getByRole("heading", { level: 3, name: /import project/i }),
    ).toBeInTheDocument();

    // Cancel
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));

    // Modal should be hidden
    expect(
      screen.queryByRole("heading", { level: 3, name: /import project/i }),
    ).not.toBeInTheDocument();
  });

  it("disables import button when no file is selected", () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    const importButton = screen.getByRole("button", { name: /^import$/i });
    expect(importButton).toBeDisabled();
  });

  it("disables import button when display name is empty", async () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    // Simulate file selection
    const file = new File(["test content"], "test-project.safx", {
      type: "application/octet-stream",
    });

    const dropZone = screen.getByText(/Drag & drop/i).closest(".drop-zone");
    if (dropZone) {
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });
    }

    await waitFor(() => {
      expect(screen.getByLabelText(/Project Name/i)).toHaveValue(
        "test-project",
      );
    });

    // Clear the auto-populated name
    const input = screen.getByLabelText(/Project Name/i);
    fireEvent.change(input, { target: { value: "" } });

    const importButton = screen.getByRole("button", { name: /^import$/i });
    expect(importButton).toBeDisabled();
  });

  it("shows error for non-.safx files", async () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    // Simulate dropping a non-.safx file
    const file = new File(["test content"], "test-project.txt", {
      type: "text/plain",
    });

    const dropZone = screen.getByText(/Drag & drop/i).closest(".drop-zone");
    if (dropZone) {
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });
    }

    await waitFor(() => {
      expect(
        screen.getByText(/Please select a .safx file/i),
      ).toBeInTheDocument();
    });
  });

  it("auto-populates display name from filename when file is dropped", async () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    const file = new File(["test content"], "my-project.safx", {
      type: "application/octet-stream",
    });

    const dropZone = screen.getByText(/Drag & drop/i).closest(".drop-zone");
    if (dropZone) {
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });
    }

    await waitFor(() => {
      expect(screen.getByLabelText(/Project Name/i)).toHaveValue("my-project");
    });
  });

  it("shows error when import name contains special characters", () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    const input = screen.getByLabelText(/Project Name/i);
    fireEvent.change(input, { target: { value: "Project!@#" } });

    expect(
      screen.getByText(/cannot contain special characters/i),
    ).toBeInTheDocument();
  });

  it("prevents import when name contains special characters", async () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    // Simulate file selection
    const file = new File(["test content"], "test-project.safx", {
      type: "application/octet-stream",
    });

    const dropZone = screen.getByText(/Drag & drop/i).closest(".drop-zone");
    if (dropZone) {
      fireEvent.drop(dropZone, {
        dataTransfer: {
          files: [file],
        },
      });
    }

    await waitFor(() => {
      expect(screen.getByLabelText(/Project Name/i)).toHaveValue(
        "test-project",
      );
    });

    // Change to invalid name
    const input = screen.getByLabelText(/Project Name/i);
    fireEvent.change(input, { target: { value: "Test!" } });

    // Try to submit
    fireEvent.click(screen.getByRole("button", { name: /^import$/i }));

    expect(mockOnImport).not.toHaveBeenCalled();
  });

  it("clears validation error in import form when special characters are removed", () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));

    const input = screen.getByLabelText(/Project Name/i);

    // Type invalid name
    fireEvent.change(input, { target: { value: "Test!" } });
    expect(
      screen.getByText(/cannot contain special characters/i),
    ).toBeInTheDocument();

    // Fix the name
    fireEvent.change(input, { target: { value: "Test" } });
    expect(
      screen.queryByText(/cannot contain special characters/i),
    ).not.toBeInTheDocument();
  });

  it("closes modal when clicking overlay", () => {
    render(<ImportExport onImport={mockOnImport} />);

    fireEvent.click(screen.getByRole("button", { name: /import project/i }));
    expect(
      screen.getByRole("heading", { level: 3, name: /import project/i }),
    ).toBeInTheDocument();

    // Click the overlay (modal-overlay class)
    const overlay = document.querySelector(".modal-overlay");
    if (overlay) {
      fireEvent.click(overlay);
    }

    expect(
      screen.queryByRole("heading", { level: 3, name: /import project/i }),
    ).not.toBeInTheDocument();
  });
});
