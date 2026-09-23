/**
 * Tests for the Pagination component.
 */
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import Pagination, { PAGE_SIZE_OPTIONS } from "../components/Pagination";

describe("Pagination", () => {
  const setup = (
    overrides: Partial<React.ComponentProps<typeof Pagination>> = {},
  ) => {
    const onPageChange = jest.fn();
    const onPageSizeChange = jest.fn();
    const currentPage = overrides.currentPage ?? 1;
    const pageSize = overrides.pageSize ?? 10;
    const totalProjects = overrides.totalProjects ?? 25;
    // Mirror what GLOW would compute server-side so tests can keep passing
    // totalProjects/pageSize and get a sensible totalPages by default.
    const totalPages =
      overrides.totalPages ?? Math.max(1, Math.ceil(totalProjects / pageSize));
    const props = {
      currentPage,
      pageSize,
      totalProjects,
      totalPages,
      onPageChange,
      onPageSizeChange,
      ...overrides,
    };
    const utils = render(<Pagination {...props} />);
    return { ...utils, onPageChange, onPageSizeChange };
  };

  it("renders current page, total pages, range, and total projects", () => {
    const { container } = setup({
      currentPage: 2,
      pageSize: 10,
      totalProjects: 25,
    });
    expect(
      container.querySelector(".pagination-current")?.textContent,
    ).toContain("2 page of 3");
    expect(container.querySelector(".pagination-total")?.textContent).toBe(
      "25",
    );
    // Range "11-20" is rendered as a single span
    expect(screen.getByText("11-20")).toBeInTheDocument();
  });

  it("disables Previous on the first page", () => {
    setup({ currentPage: 1, totalProjects: 25, pageSize: 10 });
    expect(screen.getByLabelText("Previous page")).toBeDisabled();
    expect(screen.getByLabelText("Next page")).not.toBeDisabled();
  });

  it("disables Next on the last page", () => {
    setup({ currentPage: 3, totalProjects: 25, pageSize: 10 });
    expect(screen.getByLabelText("Next page")).toBeDisabled();
    expect(screen.getByLabelText("Previous page")).not.toBeDisabled();
  });

  it("disables both nav buttons when there is only one page", () => {
    setup({ currentPage: 1, totalProjects: 5, pageSize: 10 });
    expect(screen.getByLabelText("Previous page")).toBeDisabled();
    expect(screen.getByLabelText("Next page")).toBeDisabled();
  });

  it("calls onPageChange with currentPage + 1 when Next is clicked", () => {
    const { onPageChange } = setup({
      currentPage: 1,
      totalProjects: 25,
      pageSize: 10,
    });
    fireEvent.click(screen.getByLabelText("Next page"));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("calls onPageChange with currentPage - 1 when Previous is clicked", () => {
    const { onPageChange } = setup({
      currentPage: 3,
      totalProjects: 25,
      pageSize: 10,
    });
    fireEvent.click(screen.getByLabelText("Previous page"));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("opens the page-size dropdown and lists the configured page sizes", () => {
    setup();
    fireEvent.click(screen.getByLabelText("Page size"));
    const menu = screen.getByRole("list", { name: "Page size options" });
    expect(menu).toBeInTheDocument();
    PAGE_SIZE_OPTIONS.forEach((size) => {
      expect(
        screen.getByRole("button", { name: String(size) }),
      ).toBeInTheDocument();
    });
  });

  it("calls onPageSizeChange when a new size is selected and closes dropdown", () => {
    const { onPageSizeChange } = setup({ pageSize: 10 });
    fireEvent.click(screen.getByLabelText("Page size"));
    fireEvent.click(screen.getByRole("button", { name: "20" }));
    expect(onPageSizeChange).toHaveBeenCalledWith(20);
    expect(
      screen.queryByRole("list", { name: "Page size options" }),
    ).not.toBeInTheDocument();
  });

  it("does not fire onPageSizeChange when selecting the current size", () => {
    const { onPageSizeChange } = setup({ pageSize: 10 });
    fireEvent.click(screen.getByLabelText("Page size"));
    // There are two buttons with name "10" (the toggle and the option);
    // pick the option from inside the menu.
    const menu = screen.getByRole("list", { name: "Page size options" });
    const activeOption = menu.querySelector(
      ".pagination-size-option-active",
    ) as HTMLElement;
    fireEvent.click(activeOption);
    expect(onPageSizeChange).not.toHaveBeenCalled();
  });

  it("closes the dropdown on outside click without firing a change", () => {
    const { onPageSizeChange } = setup();
    fireEvent.click(screen.getByLabelText("Page size"));
    expect(
      screen.getByRole("list", { name: "Page size options" }),
    ).toBeInTheDocument();
    fireEvent.mouseDown(document.body);
    expect(
      screen.queryByRole("list", { name: "Page size options" }),
    ).not.toBeInTheDocument();
    expect(onPageSizeChange).not.toHaveBeenCalled();
  });

  it("renders 0 total projects with both nav buttons disabled", () => {
    const { container } = setup({
      currentPage: 1,
      totalProjects: 0,
      pageSize: 10,
    });
    expect(screen.getByLabelText("Previous page")).toBeDisabled();
    expect(screen.getByLabelText("Next page")).toBeDisabled();
    expect(container.querySelector(".pagination-total")?.textContent).toBe("0");
    expect(screen.getByText("0-0")).toBeInTheDocument();
  });
});
