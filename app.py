from flask import Flask, render_template, request
import os
import pandas as pd

app = Flask(__name__)

# Uploaded files ko store karne ke liye folder
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]

    if file:
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(file_path)

        # Uploaded file ko Pandas DataFrame me read kar rahe hain
        if file.filename.lower().endswith(".csv"):
            # CSV ka separator automatically detect kar rahe hain
            df = pd.read_csv(
                file_path,
                sep=None,
                engine="python"
            )
        else:
            df = pd.read_excel(file_path)

        rows, columns = df.shape
        total_cells = rows * columns
        missing_values = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())
        column_names = df.columns.tolist()

        # Har column ki basic information nikal rahe hain
        column_details = []

        for column in df.columns:
            column_details.append({
                "name": column,
                "dtype": str(df[column].dtype),
                "non_null": int(df[column].notnull().sum()),
                "missing": int(df[column].isnull().sum()),
                "unique": int(df[column].nunique())
})

        # Numerical columns ki statistical information nikal rahe hain
        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        numeric_summary = []

        for column in numeric_columns:

            summary = df[column].describe()

            numeric_summary.append({
                "name": column,
                "count": int(summary["count"]),
                "mean": round(float(summary["mean"]), 2),
                "std": round(float(summary["std"]), 2)
                if pd.notna(summary["std"]) else 0,
                "min": round(float(summary["min"]), 2),
                "q25": round(float(summary["25%"]), 2),
                "median": round(float(summary["50%"]), 2),
                "q75": round(float(summary["75%"]), 2),
                "max": round(float(summary["max"]), 2)
            })

        # Dataset ki first 10 rows preview ke liye
        data_preview = df.head(10).to_dict(orient="records")

        return render_template(
            "analysis.html",
            filename=file.filename,
            rows=rows,
            columns=columns,
            total_cells=total_cells,
            missing_values=missing_values,
            duplicate_rows=duplicate_rows,
            column_names=column_names,
            column_details=column_details,
            numeric_summary=numeric_summary,
            data_preview=data_preview
        )

    return "No file selected."


if __name__ == "__main__":
    app.run(debug=True)