import React, { useEffect, useState } from "react";
import { icons } from "../utils/icons";
import "../styles/SolutionMetadata.css";

const DEFAULT_DESCRIPTION = "Here is the description of the solution...";

interface SolutionMetadataProps {
  /** URL to the solution application image (e.g., "/assets/application.svg"). */
  solutionImageUrl?: string;
  /** Description text for the solution. */
  solutionDescription?: string;
}

/**
 * SolutionMetadata renders the solution image (16:9, resizable) and description.
 * Falls back to a bundled inline SVG when the image URL is missing or fails to load.
 */
const SolutionMetadata: React.FC<SolutionMetadataProps> = ({
  solutionImageUrl,
  solutionDescription,
}) => {
  const [imgError, setImgError] = useState(false);
  const description = solutionDescription || DEFAULT_DESCRIPTION;
  const showImg = solutionImageUrl && !imgError;

  // Reset error state when the image URL changes so the component retries loading
  useEffect(() => {
    setImgError(false);
  }, [solutionImageUrl]);

  return (
    <div className="solution-metadata">
      <div className="solution-metadata-card">
        <div className="solution-metadata-image">
          {showImg ? (
            <img
              src={solutionImageUrl}
              alt="Solution application"
              onError={() => setImgError(true)}
            />
          ) : (
            <span
              className="awc-icon"
              dangerouslySetInnerHTML={{ __html: icons.application }}
            />
          )}
        </div>
      </div>
      <div className="solution-metadata-card">
        <div className="solution-metadata-description">
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
};

export default SolutionMetadata;
