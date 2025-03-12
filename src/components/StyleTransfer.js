import "./StyleTransfer.css";

import React, { useState } from "react";

import axios from "axios";

function StyleTransfer() {
  const [contentImage, setContentImage] = useState(null);
  const [styleImage, setStyleImage] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [contentPreview, setContentPreview] = useState(null);
  const [stylePreview, setStylePreview] = useState(null);

  // Handle content image upload
  const handleContentImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setContentImage(file);
      setContentPreview(URL.createObjectURL(file));
    }
  };

  // Handle style image upload
  const handleStyleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setStyleImage(file);
      setStylePreview(URL.createObjectURL(file));
    }
  };

  // Add the handleDownload function inside the component
  // Update the handleDownload function to handle both local and external URLs
  const handleDownload = () => {
    if (resultImage) {
      const link = document.createElement("a");
      link.href = resultImage.startsWith("http")
        ? resultImage
        : `http://localhost:5000${resultImage}`;
      link.download = "styled-image.jpg";
      link.target = "_blank";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleTransfer = async () => {
    if (!contentImage || !styleImage) {
      alert("Please upload both content and style images");
      return;
    }

    setLoading(true);
    setProgress(0);
    setResultImage(null);

    // Check if we're running on GitHub Pages
    const isGitHubPages = window.location.hostname.includes("github.io");

    if (isGitHubPages) {
      // For GitHub Pages demo, just show a mock progress
      const mockProgress = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(mockProgress);
            setLoading(false);
            // Use a placeholder image URL that's reliable
            setResultImage("https://picsum.photos/800/600");
            return 100;
          }
          return prev + 5;
        });
      }, 500);
      return;
    }

    const formData = new FormData();
    formData.append("content", contentImage);
    formData.append("style", styleImage);

    try {
      const response = await axios.post(
        "http://localhost:5000/api/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // In the handleTransfer function, change the polling interval:

      // Start polling for progress updates
      // In the handleTransfer function, modify the code that handles the completed result:

      // Modify the progress interval to check for the image when progress is high enough

      const progressInterval = setInterval(async () => {
        try {
          const progressResponse = await axios.get(
            "http://localhost:5000/api/progress"
          );
          const currentProgress = progressResponse.data.progress;
          console.log(`Progress update: ${currentProgress}%`);
          setProgress(currentProgress);

          // Try to load the image when progress is at least 50%
          if (currentProgress >= 50 && !resultImage) {
            try {
              // Check if the result image exists
              const resultUrl = `http://localhost:5000${response.data.result}`;
              console.log(
                `Checking for intermediate result at ${currentProgress}%: ${resultUrl}`
              );

              // Test if the image can be loaded
              const testImage = new Image();
              testImage.onload = () => {
                console.log(
                  `Intermediate result loaded at ${currentProgress}%`
                );
                setResultImage(response.data.result);
                // Don't set loading to false yet, keep showing progress
              };

              testImage.onerror = () => {
                console.log(
                  `No intermediate result available yet at ${currentProgress}%`
                );
                // Continue waiting
              };

              testImage.src = resultUrl + "?t=" + new Date().getTime();
            } catch (error) {
              console.log(
                `Error checking intermediate result: ${error.message}`
              );
            }
          }

          if (currentProgress >= 100) {
            clearInterval(progressInterval);

            // Add a small delay to ensure the result file is fully saved
            setTimeout(async () => {
              try {
                // Check if the result image exists
                const resultUrl = `http://localhost:5000${response.data.result}`;
                console.log(`Checking final result image at: ${resultUrl}`);

                // Test if the image can be loaded
                const testImage = new Image();
                testImage.onload = () => {
                  console.log("Final result image loaded successfully");
                  setResultImage(response.data.result);
                  setLoading(false);
                };

                testImage.onerror = async () => {
                  console.error(
                    "Error loading final result image, retrying..."
                  );
                  // Use existing retry logic
                  // Retry after a short delay with multiple attempts
                  let retryCount = 0;
                  const maxRetries = 5;

                  const retryLoadImage = () => {
                    if (retryCount < maxRetries) {
                      retryCount++;
                      console.log(
                        `Retry attempt ${retryCount} of ${maxRetries}...`
                      );

                      setTimeout(() => {
                        const newUrl = `${
                          response.data.result
                        }?retry=${retryCount}&t=${new Date().getTime()}`;
                        console.log(`Trying with URL: ${newUrl}`);
                        setResultImage(newUrl);

                        // Check if this worked
                        const retryImage = new Image();
                        retryImage.onload = () => {
                          console.log(`Retry ${retryCount} successful!`);
                          setLoading(false);
                        };

                        retryImage.onerror = () => {
                          console.log(
                            `Retry ${retryCount} failed, trying again...`
                          );
                          retryLoadImage();
                        };

                        retryImage.src = `http://localhost:5000${newUrl}`;
                      }, 2000);
                    } else {
                      console.error(
                        "Max retries reached. Could not load the result image."
                      );
                      setLoading(false);
                      alert(
                        "Could not load the result image. The style transfer might have failed."
                      );
                    }
                  };

                  retryLoadImage();
                };

                testImage.src =
                  resultUrl + "?final=true&t=" + new Date().getTime();
              } catch (error) {
                console.error("Error loading result:", error);
                setLoading(false);
              }
            }, 2000);
          }
        } catch (error) {
          console.error("Error fetching progress:", error);
        }
      }, 2000);

      // Set a timeout to clear the interval if it takes too long
      setTimeout(() => {
        clearInterval(progressInterval);
        setResultImage(response.data.result);
        setLoading(false);
      }, 120000); // 2 minutes max
    } catch (error) {
      console.error("Error:", error);
      setLoading(false);
    }
  };

  return (
    <div className="style-transfer-container">
      <h2>Neural Style Transfer</h2>
      <p>Upload a content image and a style image to transfer the style</p>

      <div className="image-upload-container">
        <div className="upload-section">
          <h3>Content Image</h3>
          <input
            type="file"
            accept="image/*"
            onChange={handleContentImageChange}
            className="file-input"
          />
          {contentPreview && (
            <div className="image-preview">
              <img src={contentPreview} alt="Content Preview" />
            </div>
          )}
        </div>

        <div className="upload-section">
          <h3>Style Image</h3>
          <input
            type="file"
            accept="image/*"
            onChange={handleStyleImageChange}
            className="file-input"
          />
          {stylePreview && (
            <div className="image-preview">
              <img src={stylePreview} alt="Style Preview" />
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handleTransfer}
        disabled={!contentImage || !styleImage || loading}
        className="transfer-button"
      >
        Transfer Style
      </button>

      {loading && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p>{progress}% Complete</p>
        </div>
      )}

      {/* Update the result image rendering to handle both local and external URLs */}

      {resultImage && (
        <div className="result-container">
          <h3>Result</h3>
          <img
            src={
              resultImage.startsWith("http")
                ? resultImage
                : `http://localhost:5000${resultImage}`
            }
            alt="Result"
            className="result-image"
          />
          <button onClick={handleDownload} className="download-button">
            Download Result
          </button>
        </div>
      )}
    </div>
  );
}

export default StyleTransfer;
