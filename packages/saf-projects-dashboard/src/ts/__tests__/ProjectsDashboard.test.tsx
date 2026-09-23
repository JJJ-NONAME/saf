/**
 * Integration tests for ProjectsDashboard pagination wiring.
 */
import React, { useState } from "react";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  act,
} from "@testing-library/react";
import ProjectsDashboard from "../components/ProjectsDashboard";
import { Project } from "../types/project";

const mockFetch = global.fetch as jest.Mock;

const makeProjects = (n: number): Project[] =>
  Array.from({ length: n }, (_, i) => ({
    name: `projects/p-${i + 1}`,
    display_name: `Project ${i + 1}`,
  }));

/**
 * Mock the GLOW paginated `/projects` response. By default the slice and the
 * pagination metadata are computed from `total` and `pageSize` so tests can
 * keep specifying the dataset size instead of the full payload.
 */
const mockListResponse = (
  total: number,
  page: number = 1,
  pageSize: number = 10,
) => {
  const all = makeProjects(total);
  const start = Math.max(0, (page - 1) * pageSize);
  const projects = all.slice(start, start + pageSize);
  const total_pages = Math.max(1, Math.ceil(total / pageSize));
  mockFetch.mockResolvedValueOnce({
    ok: true,
    headers: { get: () => "application/json" },
    json: async () => ({
      projects,
      current_page: page,
      total_pages,
      page_size: pageSize,
      total_projects: total,
    }),
  });
};

/**
 * Wrapper that holds dashboard props in local state and forwards `setProps`,
 * mirroring the Dash runtime so the component behaves as a controlled tree.
 */
const Harness: React.FC<{ initialProps?: Record<string, unknown> }> = ({
  initialProps = {},
}) => {
  const [state, setState] = useState<Record<string, unknown>>({
    id: "dashboard",
    pageSize: 10,
    ...initialProps,
  });
  const setProps = (patch: Record<string, unknown>) =>
    setState((prev) => ({ ...prev, ...patch }));
  const Component = ProjectsDashboard as unknown as React.FC<
    Record<string, unknown>
  >;
  return <Component {...state} setProps={setProps} />;
};

const getPaginationTotal = () =>
  document.querySelector(".pagination-total")?.textContent ?? "";

const getPaginationCurrent = () =>
  document.querySelector(".pagination-current")?.textContent ?? "";

describe("ProjectsDashboard pagination", () => {
  let openSpy: jest.SpyInstance;

  beforeEach(() => {
    mockFetch.mockReset();
    openSpy = jest.spyOn(globalThis, "open").mockImplementation(() => null);
  });

  afterEach(() => {
    openSpy.mockRestore();
  });

  it("loads the first page on mount and renders pagination summary", async () => {
    mockListResponse(25);

    render(<Harness />);

    await waitFor(() => {
      expect(getPaginationTotal()).toBe("25");
    });
    expect(getPaginationCurrent()).toContain("1 page of 3");
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it("re-fetches when Next is clicked and updates currentPage", async () => {
    mockListResponse(25, 1, 10);
    mockListResponse(25, 2, 10);

    render(<Harness />);

    await waitFor(() => expect(getPaginationTotal()).toBe("25"));

    await act(async () => {
      fireEvent.click(screen.getByLabelText("Next page"));
    });

    await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));
    expect(getPaginationCurrent()).toContain("2 page of 3");
  });

  it("resets to page 1 and re-fetches when page size changes", async () => {
    mockListResponse(25, 2, 10);
    mockListResponse(25, 1, 20);
    mockListResponse(25, 1, 20);

    render(<Harness initialProps={{ currentPage: 2, pageSize: 10 }} />);

    await waitFor(() => expect(getPaginationTotal()).toBe("25"));
    const callsAfterMount = mockFetch.mock.calls.length;

    await act(async () => {
      fireEvent.click(screen.getByLabelText("Page size"));
    });
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "20" }));
    });

    await waitFor(() =>
      expect(mockFetch.mock.calls.length).toBeGreaterThan(callsAfterMount),
    );

    expect(getPaginationCurrent()).toContain("1 page of 2");
  });

  it("does not show pagination while loading or when there are no projects", async () => {
    mockListResponse(0);

    render(<Harness />);

    await waitFor(() =>
      expect(document.querySelector(".pagination")).not.toBeInTheDocument(),
    );
    expect(screen.queryByLabelText("Next page")).not.toBeInTheDocument();
  });

  it("opens and closes the ProjectInfo modal from the info button", async () => {
    mockListResponse(2);

    render(<Harness />);

    await waitFor(() => expect(getPaginationTotal()).toBe("2"));

    fireEvent.click(
      screen.getAllByRole("button", { name: /project info/i })[0],
    );

    expect(screen.getByText("Project ID:")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { level: 3, name: "Project 1" }),
    ).toBeInTheDocument();
    expect(screen.getByText("projects/p-1")).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: /close project information/i }),
    );

    expect(screen.queryByText("Project ID:")).not.toBeInTheDocument();
  });

  it("opens the project when Open is clicked in ProjectInfo modal", async () => {
    mockListResponse(1);

    render(<Harness />);

    await waitFor(() => expect(getPaginationTotal()).toBe("1"));

    fireEvent.click(screen.getByRole("button", { name: /project info/i }));
    fireEvent.click(screen.getByRole("button", { name: "Open" }));

    expect(openSpy).toHaveBeenCalledWith(
      `${window.location.origin}/projects/p-1`,
      "_self",
    );
  });

  it("closes ProjectInfo modal when clicking outside", async () => {
    mockListResponse(1);

    const { container } = render(<Harness />);

    await waitFor(() => expect(getPaginationTotal()).toBe("1"));

    fireEvent.click(screen.getByRole("button", { name: /project info/i }));
    expect(screen.getByText("Project ID:")).toBeInTheDocument();

    const overlay = container.querySelector(".modal-overlay") as HTMLElement;
    fireEvent.click(overlay);

    expect(screen.queryByText("Project ID:")).not.toBeInTheDocument();
  });

  it("navigates to documentation when help button is clicked", async () => {
    mockListResponse(1);

    render(<Harness />);

    await waitFor(() => expect(getPaginationTotal()).toBe("1"));

    fireEvent.click(
      screen.getByRole("button", { name: /documentation help/i }),
    );

    expect(openSpy).toHaveBeenCalledWith(
      `${window.location.origin}/documentation/index.html`,
      "_self",
    );
  });

  it("sends updated description in edit payload", async () => {
    mockListResponse(1);

    const updatedProject: Project = {
      name: "projects/p-1",
      display_name: "Renamed Project",
      description: "Updated description",
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => updatedProject,
    });

    render(
      <Harness
        initialProps={{
          selectedProject: {
            name: "projects/p-1",
            display_name: "Project 1",
            description: "Old description",
          },
        }}
      />,
    );

    await waitFor(() => expect(getPaginationTotal()).toBe("1"));

    fireEvent.change(screen.getByLabelText(/Project Name/i), {
      target: { value: "Renamed Project" },
    });
    fireEvent.change(screen.getByLabelText(/Project Description/i), {
      target: { value: "Updated description" },
    });
    fireEvent.click(screen.getByRole("button", { name: /update/i }));

    await waitFor(() => expect(mockFetch).toHaveBeenCalledTimes(2));

    expect(mockFetch).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining("/projects/p-1"),
      expect.objectContaining({
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          display_name: "Renamed Project",
          description: "Updated description",
        }),
      }),
    );
  });
});
