/**
 * Tests for ProjectsTable component
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ProjectsTable from "../components/ProjectsTable";
import { Project } from "../types/project";

describe("ProjectsTable", () => {
  const mockProjects: Project[] = [
    {
      name: "projects/test-1",
      display_name: "Test Project 1",
      date_created: "2025-01-01T10:00:00Z",
      date_modified: "2025-01-15T14:30:00Z",
    },
    {
      name: "projects/test-2",
      display_name: "Test Project 2",
    },
  ];

  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();
  const mockOnExport = jest.fn();
  const mockOnCardClick = jest.fn();
  const mockOnFavoriteToggle = jest.fn();
  const mockOnInfo = jest.fn();
  const emptyFavorites: string[] = [];

  const defaultProps = {
    onEdit: mockOnEdit,
    onDelete: mockOnDelete,
    onExport: mockOnExport,
    onCardClick: mockOnCardClick,
    onFavoriteToggle: mockOnFavoriteToggle,
    onInfo: mockOnInfo,
    favoriteIds: emptyFavorites,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders empty state when no projects", () => {
    render(<ProjectsTable projects={[]} {...defaultProps} />);

    expect(screen.getByText(/No projects found/i)).toBeInTheDocument();
    expect(screen.getByText(/Create your first project/i)).toBeInTheDocument();
  });

  it("renders a table with column headers", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    expect(screen.getByRole("table")).toBeInTheDocument();
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Created")).toBeInTheDocument();
    expect(screen.getByText("Last Saved")).toBeInTheDocument();
  });

  it("renders project rows with correct information", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    expect(screen.getByText("Test Project 1")).toBeInTheDocument();
    expect(screen.getByText("Test Project 2")).toBeInTheDocument();
  });

  it("displays formatted dates when available", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    expect(screen.getByText("01/01/2025 10:00 AM")).toBeInTheDocument();
    expect(screen.getByText("01/15/2025 02:30 PM")).toBeInTheDocument();
  });

  it("calls onCardClick when a row is clicked", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const rows = screen
      .getAllByRole("row")
      .filter((row) => row.classList.contains("projects-table-row"));
    fireEvent.click(rows[0]);

    expect(mockOnCardClick).toHaveBeenCalledWith("projects/test-1");
  });

  it("calls onCardClick when Enter is pressed on a row", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const rows = screen
      .getAllByRole("row")
      .filter((row) => row.classList.contains("projects-table-row"));
    fireEvent.keyDown(rows[0], { key: "Enter" });

    expect(mockOnCardClick).toHaveBeenCalledWith("projects/test-1");
  });

  it("calls onCardClick when Space is pressed on a row", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const rows = screen
      .getAllByRole("row")
      .filter((row) => row.classList.contains("projects-table-row"));
    fireEvent.keyDown(rows[0], { key: " " });

    expect(mockOnCardClick).toHaveBeenCalledWith("projects/test-1");
  });

  it("does not call onCardClick when info button is clicked", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const infoButtons = screen.getAllByRole("button", {
      name: /project info/i,
    });
    fireEvent.click(infoButtons[0]);

    expect(mockOnInfo).toHaveBeenCalledWith("projects/test-1");
    expect(mockOnCardClick).not.toHaveBeenCalled();
  });

  it("calls onEdit via context menu", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[0]);
    const editItem = screen.getByRole("menuitem", { name: /edit/i });
    fireEvent.click(editItem);

    expect(mockOnEdit).toHaveBeenCalledWith(mockProjects[0]);
    expect(mockOnCardClick).not.toHaveBeenCalled();
  });

  it("calls onExport via context menu", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[1]);
    const exportItem = screen.getByRole("menuitem", { name: /export/i });
    fireEvent.click(exportItem);

    expect(mockOnExport).toHaveBeenCalledWith("projects/test-2");
    expect(mockOnCardClick).not.toHaveBeenCalled();
  });

  it("calls onDelete via context menu", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[0]);
    const deleteItem = screen.getByRole("menuitem", { name: /delete/i });
    fireEvent.click(deleteItem);

    expect(mockOnDelete).toHaveBeenCalledWith("projects/test-1");
    expect(mockOnCardClick).not.toHaveBeenCalled();
  });

  it("sets correct aria-label on each row", () => {
    render(<ProjectsTable projects={mockProjects} {...defaultProps} />);

    expect(
      screen.getByRole("row", { name: /open project test project 1/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("row", { name: /open project test project 2/i }),
    ).toBeInTheDocument();
  });
});
