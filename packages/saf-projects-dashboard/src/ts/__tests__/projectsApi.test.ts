/**
 * Tests for projectsApi client
 */
import { projectsApi } from "../api/projectsApi";
import { PaginatedProjects, Project } from "../types/project";

describe("projectsApi", () => {
  const mockFetch = global.fetch as jest.Mock;

  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe("listProjects", () => {
    const makePage = (
      overrides: Partial<PaginatedProjects> = {},
    ): PaginatedProjects => ({
      projects: [
        { name: "projects/1", display_name: "Project 1" },
        { name: "projects/2", display_name: "Project 2" },
      ],
      current_page: 1,
      total_pages: 1,
      page_size: 10,
      total_projects: 2,
      ...overrides,
    });

    it("fetches the default page when no pagination args are provided", async () => {
      const page = makePage();

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      const result = await projectsApi.listProjects();

      expect(mockFetch).toHaveBeenCalledWith("/projects", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      expect(result).toEqual(page);
    });

    it("forwards page and page_size as query params", async () => {
      const page = makePage({
        current_page: 2,
        total_pages: 5,
        page_size: 10,
        total_projects: 42,
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      const result = await projectsApi.listProjects(2, 10);

      expect(mockFetch).toHaveBeenCalledWith("/projects?page=2&page_size=10", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      expect(result).toEqual(page);
    });

    it("forwards date filter params as snake_case query params", async () => {
      const page = makePage({ total_projects: 1, projects: [] });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      await projectsApi.listProjects(undefined, undefined, {
        dateCreatedFrom: "2025-01-01",
        dateCreatedTo: "2025-06-30",
        dateModifiedFrom: "2025-03-01",
        dateModifiedTo: "2025-03-31",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        "/projects?filter=date_created+%3E%3D+2025-01-01+AND+date_created+%3C%3D+2025-06-30+AND+date_modified+%3E%3D+2025-03-01+AND+date_modified+%3C%3D+2025-03-31",
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    it("forwards search filter as display_name query expression", async () => {
      const page = makePage({ total_projects: 1, projects: [] });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      await projectsApi.listProjects(undefined, undefined, {
        search: "Motor Project",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        "/projects?filter=display_name+%3D+%22Motor+Project%22",
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    it("forwards only set filter params", async () => {
      const page = makePage();

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      await projectsApi.listProjects(undefined, undefined, {
        dateCreatedFrom: "2025-01-01",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        "/projects?filter=date_created+%3E%3D+2025-01-01",
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    it("combines pagination and filter query params", async () => {
      const page = makePage({
        current_page: 1,
        total_pages: 1,
        page_size: 15,
        total_projects: 3,
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      await projectsApi.listProjects(1, 15, {
        dateCreatedFrom: "2025-01-01",
        dateCreatedTo: "2025-12-31",
      });

      expect(mockFetch).toHaveBeenCalledWith(
        "/projects?page=1&page_size=15&filter=date_created+%3E%3D+2025-01-01+AND+date_created+%3C%3D+2025-12-31",
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
        },
      );
    });

    it("does not append an empty filter query param", async () => {
      const page = makePage();

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => page,
      });

      await projectsApi.listProjects(undefined, undefined, {});

      expect(mockFetch).toHaveBeenCalledWith("/projects", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
    });

    it("throws error on failure", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
        json: async () => ({ detail: "Server error" }),
      });

      await expect(projectsApi.listProjects()).rejects.toThrow("Server error");
    });
  });

  describe("createProject", () => {
    it("creates project with display name", async () => {
      const mockProject: Project = {
        name: "projects/new-123",
        display_name: "New Project",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => mockProject,
      });

      const result = await projectsApi.createProject("New Project");

      expect(mockFetch).toHaveBeenCalledWith("/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ display_name: "New Project", description: "" }),
      });
      expect(result).toEqual(mockProject);
    });
  });

  describe("getProject", () => {
    it("fetches single project", async () => {
      const mockProject: Project = {
        name: "/123",
        display_name: "Test Project",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => mockProject,
      });

      const result = await projectsApi.getProject("123");

      expect(mockFetch).toHaveBeenCalledWith("/123", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      expect(result).toEqual(mockProject);
    });
  });

  describe("updateProject", () => {
    it("updates project display name", async () => {
      const mockProject: Project = {
        name: "/123",
        display_name: "Updated Name",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => mockProject,
      });

      const result = await projectsApi.updateProject(
        "123",
        "Updated Name",
        "Updated Description",
      );

      expect(mockFetch).toHaveBeenCalledWith("/123", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          display_name: "Updated Name",
          description: "Updated Description",
        }),
      });
      expect(result).toEqual(mockProject);
    });
  });

  describe("deleteProject", () => {
    it("deletes project", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => null },
      });

      await projectsApi.deleteProject("123");

      expect(mockFetch).toHaveBeenCalledWith("/123", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
    });

    it("throws error when project not found", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
        json: async () => ({ detail: "Project not found" }),
      });

      await expect(projectsApi.deleteProject("nonexistent")).rejects.toThrow(
        "Project not found",
      );
    });
  });

  describe("exportProject", () => {
    it("exports project as blob", async () => {
      const mockBlob = new Blob(["test data"], {
        type: "application/octet-stream",
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        blob: async () => mockBlob,
      });

      const result = await projectsApi.exportProject("123");

      expect(mockFetch).toHaveBeenCalledWith("/123:export", {
        method: "GET",
      });
      expect(result).toEqual(mockBlob);
    });
  });

  describe("importProject", () => {
    it("imports project from base64 content", async () => {
      const mockProject: Project = {
        name: "projects/imported-123",
        display_name: "Imported Project",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => mockProject,
      });

      const base64Content =
        "data:application/octet-stream;base64,SGVsbG8gV29ybGQ=";
      const result = await projectsApi.importProject(
        base64Content,
        "test.safx",
        "Imported Project",
      );

      expect(mockFetch).toHaveBeenCalledWith(
        "/projects:import",
        expect.objectContaining({
          method: "POST",
          body: expect.any(FormData),
        }),
      );
      expect(result).toEqual(mockProject);
    });
  });

  describe("upgradeProject", () => {
    it("upgrades project", async () => {
      const mockProject: Project = {
        name: "/123",
        display_name: "Upgraded Project",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => mockProject,
      });

      const result = await projectsApi.upgradeProject("123");

      expect(mockFetch).toHaveBeenCalledWith("/123:upgrade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      expect(result).toEqual(mockProject);
    });
  });
});
