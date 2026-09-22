/**
 * Tests for ProjectForm component
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ProjectForm from "../components/ProjectForm";
import { Project } from "../types/project";

describe("ProjectForm", () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  const existingProject: Project = {
    name: "projects/test-123",
    display_name: "Existing Project",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("Create mode (no project prop)", () => {
    it("renders create form with empty input", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      expect(screen.getByText("Create New Project")).toBeInTheDocument();
      expect(screen.getByLabelText(/Project Name/i)).toHaveValue("");
      expect(
        screen.getByRole("button", { name: /create/i }),
      ).toBeInTheDocument();
    });

    it("shows error when submitting empty name", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      fireEvent.click(screen.getByRole("button", { name: /create/i }));

      expect(screen.getByText("Project name is required")).toBeInTheDocument();
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("calls onSubmit with trimmed name", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, { target: { value: "  New Project  " } });
      fireEvent.click(screen.getByRole("button", { name: /create/i }));

      expect(mockOnSubmit).toHaveBeenCalledWith("New Project", "");
    });

    it("calls onCancel when Cancel button is clicked", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      fireEvent.click(screen.getByRole("button", { name: /cancel/i }));

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it("clears error when user starts typing", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      // Trigger error
      fireEvent.click(screen.getByRole("button", { name: /create/i }));
      expect(screen.getByText("Project name is required")).toBeInTheDocument();

      // Start typing
      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, { target: { value: "a" } });

      expect(
        screen.queryByText("Project name is required"),
      ).not.toBeInTheDocument();
    });
  });

  describe("Name validation", () => {
    it("shows error when name contains special characters", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, { target: { value: "Project!@#" } });

      expect(
        screen.getByText(/cannot contain special characters/i),
      ).toBeInTheDocument();
    });

    it("prevents submit when name contains special characters", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, { target: { value: "Test Project!" } });
      fireEvent.click(screen.getByRole("button", { name: /create/i }));

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it("clears validation error when special characters are removed", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

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

    it.each(["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "+", ">", "<"])(
      "rejects name containing '%s'",
      (char) => {
        render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

        const input = screen.getByLabelText(/Project Name/i);
        fireEvent.change(input, { target: { value: `Project${char}Name` } });

        expect(
          screen.getByText(/cannot contain special characters/i),
        ).toBeInTheDocument();
      },
    );

    it("allows valid names with letters, numbers, spaces, hyphens", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, {
        target: { value: "My Project-2 v3.0" },
      });

      expect(
        screen.queryByText(/cannot contain special characters/i),
      ).not.toBeInTheDocument();
    });
  });

  describe("Edit mode (with project prop)", () => {
    it("renders edit form with existing name", () => {
      render(
        <ProjectForm
          project={existingProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );

      expect(screen.getByText("Edit Project")).toBeInTheDocument();
      expect(screen.getByLabelText(/Project Name/i)).toHaveValue(
        "Existing Project",
      );
      expect(
        screen.getByRole("button", { name: /update/i }),
      ).toBeInTheDocument();
    });

    it("displays project ID in info section", () => {
      render(
        <ProjectForm
          project={existingProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );

      expect(screen.getByText("Project ID:")).toBeInTheDocument();
      expect(screen.getByText("projects/test-123")).toBeInTheDocument();
    });

    it("calls onSubmit with updated name", () => {
      render(
        <ProjectForm
          project={existingProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );

      const input = screen.getByLabelText(/Project Name/i);
      fireEvent.change(input, { target: { value: "Updated Project Name" } });
      fireEvent.click(screen.getByRole("button", { name: /update/i }));

      expect(mockOnSubmit).toHaveBeenCalledWith("Updated Project Name", "");
    });
  });
});
