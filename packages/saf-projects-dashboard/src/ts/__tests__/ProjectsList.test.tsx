/**
 * Tests for ProjectsList component
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import ProjectsList from "../components/ProjectsList";
import { Project } from "../types/project";

describe("ProjectsList", () => {
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
    render(<ProjectsList projects={[]} {...defaultProps} />);

    expect(screen.getByText(/No projects found/i)).toBeInTheDocument();
    expect(screen.getByText(/Create your first project/i)).toBeInTheDocument();
  });

  it("renders project cards with correct information", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Check first project
    expect(screen.getAllByText("Test Project 1").length).toBeGreaterThan(0);

    // Check second project
    expect(screen.getAllByText("Test Project 2").length).toBeGreaterThan(0);
  });

  it("calls onEdit when Edit button is clicked", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Open the context menu first, then click Edit
    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[0]);
    const editButton = screen.getByRole("menuitem", { name: /edit/i });
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(mockProjects[0]);
  });

  it("calls onDelete when Delete button is clicked", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Open the context menu first, then click Delete
    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[0]);
    const deleteButton = screen.getByRole("menuitem", { name: /delete/i });
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith("projects/test-1");
  });

  it("calls onExport when Export button is clicked", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Open the context menu on the second card, then click Export
    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[1]);
    const exportButton = screen.getByRole("menuitem", { name: /export/i });
    fireEvent.click(exportButton);

    expect(mockOnExport).toHaveBeenCalledWith("projects/test-2");
  });

  it("displays date information when available", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Check that dates are formatted as dd/mm/yyyy
    expect(screen.getAllByText(/Created:/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Last Saved:/i).length).toBeGreaterThan(0);
    expect(screen.getByText("01/01/2025 10:00 AM")).toBeInTheDocument();
    expect(screen.getByText("01/15/2025 02:30 PM")).toBeInTheDocument();
  });

  it("calls onCardClick when card is clicked", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    const cards = screen.getAllByRole("article");
    fireEvent.click(cards[0]);

    expect(mockOnCardClick).toHaveBeenCalledWith("projects/test-1");
  });

  it("does not call onCardClick when action buttons are clicked", () => {
    render(<ProjectsList projects={mockProjects} {...defaultProps} />);

    // Open context menu and click Edit — should not trigger card click
    const moreButtons = screen.getAllByRole("button", {
      name: /more actions/i,
    });
    fireEvent.click(moreButtons[0]);
    const editButton = screen.getByRole("menuitem", { name: /edit/i });
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalled();
    expect(mockOnCardClick).not.toHaveBeenCalled();
  });
});
