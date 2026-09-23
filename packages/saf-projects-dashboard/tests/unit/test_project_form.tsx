import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ProjectForm from "../../src/ts/components/ProjectForm";
import { Project } from "../../src/ts/types/project";

describe("ProjectForm Component", () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  describe("Create Mode", () => {
    test("renders form with 'Create New Project' title", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      expect(screen.getByText("Create New Project")).toBeInTheDocument();
    });

    test("renders empty description textarea", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      ) as HTMLTextAreaElement;
      expect(descriptionTextarea).toHaveValue("");
      expect(descriptionTextarea).toBeInstanceOf(HTMLTextAreaElement);
      expect(descriptionTextarea.rows).toBe(2);
    });

    test("displays word count as 0 / 200 initially", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      expect(screen.getByText("0 / 200 words")).toBeInTheDocument();
    });

    test("updates word count when description changes", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      );

      await user.type(descriptionTextarea, "Hello world test");
      expect(screen.getByText("3 / 200 words")).toBeInTheDocument();
    });

    test("prevents exceeding 200 words", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      ) as HTMLTextAreaElement;

      // Create text with 201 words
      const longText = Array(201).fill("word").join(" ");
      await user.type(descriptionTextarea, longText);

      // Verify that the value does not exceed 200 words
      const words = descriptionTextarea.value
        .trim()
        .split(/\s+/)
        .filter((w) => w.length > 0);
      expect(words.length).toBeLessThanOrEqual(200);
    });

    test("submits form with display name and description", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const nameInput = screen.getByPlaceholderText("Enter project name");
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      );
      const submitButton = screen.getByRole("button", { name: "Create" });

      await user.type(nameInput, "Test Project");
      await user.type(descriptionTextarea, "Test description");
      await user.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith(
        "Test Project",
        "Test description",
      );
    });

    test("does not submit without project name", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      );
      const submitButton = screen.getByRole("button", { name: "Create" });

      await user.type(descriptionTextarea, "Test description");
      await user.click(submitButton);

      expect(mockOnSubmit).not.toHaveBeenCalled();
      expect(screen.getByText("Project name is required")).toBeInTheDocument();
    });
  });

  describe("Edit Mode", () => {
    const mockProject: Project = {
      name: "project-123",
      display_name: "Test Project",
      description: "This is a test project with a description",
      date_created: "2024-01-01T00:00:00Z",
      date_modified: "2024-01-02T00:00:00Z",
    };

    test("renders form with 'Edit Project' title", () => {
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      expect(screen.getByText("Edit Project")).toBeInTheDocument();
    });

    test("pre-fills description in edit mode", () => {
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      const descriptionTextarea = screen.getByDisplayValue(
        "This is a test project with a description",
      ) as HTMLTextAreaElement;
      expect(descriptionTextarea).toBeInTheDocument();
      expect(descriptionTextarea).toBeInstanceOf(HTMLTextAreaElement);
    });

    test("displays correct word count for pre-filled description", () => {
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      expect(screen.getByText("7 / 200 words")).toBeInTheDocument();
    });

    test("updates description in edit mode", async () => {
      const user = userEvent.setup();
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      const descriptionTextarea = screen.getByDisplayValue(
        "This is a test project with a description",
      ) as HTMLTextAreaElement;

      await user.clear(descriptionTextarea);
      await user.type(descriptionTextarea, "Updated description");

      expect(screen.getByText("2 / 200 words")).toBeInTheDocument();
    });

    test("shows Update button in edit mode", () => {
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      expect(
        screen.getByRole("button", { name: "Update" }),
      ).toBeInTheDocument();
    });

    test("displays project ID in edit mode", () => {
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );
      expect(screen.getByText("project-123")).toBeInTheDocument();
    });

    test("submits form with updated description", async () => {
      const user = userEvent.setup();
      render(
        <ProjectForm
          project={mockProject}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />,
      );

      const descriptionTextarea = screen.getByDisplayValue(
        "This is a test project with a description",
      ) as HTMLTextAreaElement;
      const submitButton = screen.getByRole("button", { name: "Update" });

      await user.clear(descriptionTextarea);
      await user.type(descriptionTextarea, "New description");
      await user.click(submitButton);

      expect(mockOnSubmit).toHaveBeenCalledWith(
        "Test Project",
        "New description",
      );
    });
  });

  describe("Common Functionality", () => {
    test("cancel button calls onCancel", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      const cancelButton = screen.getByRole("button", { name: "Cancel" });

      await user.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });

    test("textarea has 2 rows", () => {
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      ) as HTMLTextAreaElement;
      expect(descriptionTextarea.rows).toBe(2);
    });

    test("clears form after successful submission", async () => {
      const user = userEvent.setup();
      render(<ProjectForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const nameInput = screen.getByPlaceholderText(
        "Enter project name",
      ) as HTMLInputElement;
      const descriptionTextarea = screen.getByPlaceholderText(
        "Enter project description",
      ) as HTMLTextAreaElement;
      const submitButton = screen.getByRole("button", { name: "Create" });

      await user.type(nameInput, "Test Project");
      await user.type(descriptionTextarea, "Test description");
      await user.click(submitButton);

      // Form should be cleared after submission
      await waitFor(() => {
        expect(nameInput.value).toBe("");
        expect(descriptionTextarea.value).toBe("");
      });
    });
  });
});
