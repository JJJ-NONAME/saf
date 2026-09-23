import React, { useState } from "react";
import { icons } from "../utils/icons";

/**
 * Format a date string as dd/mm/yyyy.
 * @param dateString - ISO 8601 date string
 * @returns Formatted date string or "N/A" if undefined
 */
export const formatDate = (dateString?: string): string => {
  if (!dateString) return "N/A";
  const d = new Date(dateString);
  const month = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  const year = d.getUTCFullYear();
  let hours = d.getUTCHours();
  const minutes = String(d.getUTCMinutes()).padStart(2, "0");
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12;
  const hh = String(hours).padStart(2, "0");
  return `${month}/${day}/${year} ${hh}:${minutes} ${ampm}`;
};

/**
 * ProjectIcon renders the icon for a project card or row.
 * Uses React state for fallback instead of DOM mutation.
 */
export const ProjectIcon: React.FC<{ src?: string }> = ({ src }) => {
  const [error, setError] = useState(false);

  if (src && !error) {
    return (
      <img
        className="project-card-icon"
        src={src}
        alt=""
        key={src}
        onError={() => setError(true)}
      />
    );
  }

  return (
    <span
      className="awc-icon project-card-icon"
      dangerouslySetInnerHTML={{ __html: icons.project }}
    />
  );
};
