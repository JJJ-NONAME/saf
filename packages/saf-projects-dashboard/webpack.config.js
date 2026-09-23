const path = require("path");
const { BundleAnalyzerPlugin } = require("webpack-bundle-analyzer");

const pythonModuleName = "ansys_saf_projects_dashboard";

module.exports = function (env, argv) {
  const mode = (argv && argv.mode) || "production";
  const analyze = env && env.analyze;
  const entry = [path.join(__dirname, "src/ts/index.ts")];
  const output = {
    path: path.join(__dirname, "src", pythonModuleName),
    filename: `${pythonModuleName}.js`,
    library: pythonModuleName,
    libraryTarget: "umd",
  };

  // Bundle analyzer plugin (only when --env analyze is passed)
  const plugins = analyze
    ? [
        new BundleAnalyzerPlugin({
          analyzerMode: "static",
          reportFilename: "bundle-analysis.html",
          openAnalyzer: true,
          generateStatsFile: true,
          statsFilename: "bundle-stats.json",
        }),
      ]
    : [];

  const externals = {
    react: {
      commonjs: "react",
      commonjs2: "react",
      amd: "react",
      umd: "react",
      root: "React",
    },
    "react-dom": {
      commonjs: "react-dom",
      commonjs2: "react-dom",
      amd: "react-dom",
      umd: "react-dom",
      root: "ReactDOM",
    },
  };

  return {
    output,
    mode,
    entry,
    target: "web",
    externals,
    resolve: {
      extensions: [".ts", ".tsx", ".js", ".jsx", ".json"],
    },
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: "ts-loader",
          exclude: /node_modules/,
        },
        {
          test: /\.css$/,
          use: [
            {
              loader: "style-loader",
              options: {
                insert: function insertAtTop(element) {
                  var parent = document.querySelector("head");
                  var lastInsertedElement =
                    window._lastElementInsertedByStyleLoader;

                  if (!lastInsertedElement) {
                    parent.insertBefore(element, parent.firstChild);
                  } else if (lastInsertedElement.nextSibling) {
                    parent.insertBefore(
                      element,
                      lastInsertedElement.nextSibling,
                    );
                  } else {
                    parent.appendChild(element);
                  }

                  window._lastElementInsertedByStyleLoader = element;
                },
              },
            },
            {
              loader: "css-loader",
            },
          ],
        },
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/,
          type: "asset/resource",
          generator: {
            filename: "assets/fonts/[name][ext]",
          },
        },
        {
          test: /\.svg$/,
          type: "asset/source",
        },
      ],
    },
    plugins,
  };
};
