import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ProjectInfo from "../components/ProjectInfo";
import { Project } from "../types/project";

describe("ProjectInfo", () => {
  const mockOnClose = jest.fn();
  const mockOnOpen = jest.fn();

  const project: Project = {
    name: "projects/test-123",
    display_name: "Test Project",
    date_created: "2025-01-01T10:00:00Z",
    date_modified: "2025-01-15T14:30:00Z",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders project metadata", () => {
    render(
      <ProjectInfo
        project={project}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
      />,
    );

    expect(screen.getByText("Test Project")).toBeInTheDocument();
    expect(screen.getByText("Project ID:")).toBeInTheDocument();
    expect(screen.getByText("projects/test-123")).toBeInTheDocument();
    expect(screen.getByText("Created:")).toBeInTheDocument();
    expect(screen.getByText("Modified:")).toBeInTheDocument();
    expect(screen.getByText("01/01/2025 10:00 AM")).toBeInTheDocument();
    expect(screen.getByText("01/15/2025 02:30 PM")).toBeInTheDocument();
  });

  it("calls onOpen when Open is clicked", () => {
    render(
      <ProjectInfo
        project={project}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Open" }));

    expect(mockOnOpen).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when X is clicked", () => {
    render(
      <ProjectInfo
        project={project}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: /close project information/i }),
    );

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when overlay is clicked", () => {
    const { container } = render(
      <ProjectInfo
        project={project}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
      />,
    );

    const overlay = container.querySelector(".modal-overlay") as HTMLElement;
    fireEvent.click(overlay);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it("does not close when clicking inside modal content", () => {
    render(
      <ProjectInfo
        project={project}
        onClose={mockOnClose}
        onOpen={mockOnOpen}
      />,
    );

    fireEvent.click(screen.getByText("Project ID:"));

    expect(mockOnClose).not.toHaveBeenCalled();
  });
});
