mod cli;
mod schema;
use crate::{
    cli::NonEmptyDirAction,
    schema::{CodeCell, MimeBundle, RawNotebook, SourceValue},
};
use anyhow::{anyhow, bail};
use base64::prelude::*;
use clap::Parser;
use colored::Colorize;
use std::{
    fs::{create_dir_all, remove_dir_all, File},
    io::{BufReader, BufWriter, Write},
    path::Path,
};
static TO_TRIM: &[char] = &['-', ' ', '_'];
#[derive(Debug, Clone)]
struct ToWrite<'a> {
    image_type: ImageType,
    image_json_data: &'a SourceValue,
    name: String,
}
fn main() -> anyhow::Result<()> {
    let cli = cli::Cli::parse();
    let file = File::open(&cli.file)?;
    let nb: RawNotebook = serde_json::from_reader(BufReader::new(file))?;
    let tag_prefix = cli
        .tag_prefix
        .as_deref()
        .unwrap_or("img")
        .trim_end_matches(TO_TRIM)
        .to_owned();
    let output_path = match cli.output_path {
        Some(ref output_path) => output_path.clone(),
        None => {
            let file_stem = cli
                .file
                .file_stem()
                .ok_or_else(|| anyhow!("Input filename is empty"))?
                .to_str()
                .ok_or_else(|| anyhow!("Bad file name"))?; // can't see how to manipulate OsStr themselves
            let Some(parent) = cli.file.parent() else {
                bail!("Invalid output path".red());
            };
            parent.join(file_stem.to_owned() + "_images")
        }
    };
    let n_cells = nb.cells.len();
    // https://stackoverflow.com/a/69298721
    let n_digits = n_cells.checked_ilog10().unwrap_or(0) + 1;
    let mut to_write = Vec::new();
    for (i, cell) in nb
        .cells
        .iter()
        .enumerate()
        .filter_map(|(j, cc)| cc.get_code_cell().map(|c| (j, c)))
    {
        let image_name = get_image_candidate(cell, &tag_prefix)
            .unwrap_or_else(|| format!("img-{:0width$}", i + 1, width = n_digits as usize));

        let cell_images: Vec<_> = cell
            .get_output_data()
            .iter()
            .flat_map(|mb| get_image_data(mb))
            .collect();
        let n_cell_images = cell_images.len();
        to_write.extend(cell_images.iter().enumerate().map(
            |(j, (image_type, image_json_data))| ToWrite {
                image_type: *image_type,
                image_json_data,
                name: {
                    if n_cell_images > 1 {
                        let n_img_digits = n_cell_images.checked_ilog10().unwrap_or(0) + 1;
                        format!(
                            "{}-{:0width$}",
                            image_name,
                            j + 1,
                            width = n_img_digits as usize
                        )
                    } else {
                        image_name.clone()
                    }
                },
            },
        ));
    }
    if !to_write.is_empty() {
        checked_create_dir(&output_path, cli.non_empty_action.get_action(), cli.dry_run)?;
    }
    for item in to_write {
        let file_name = output_path
            .join(item.name)
            .with_extension(item.image_type.get_extension());
        if !cli.quiet {
            make_write_message(&cli, &file_name);
        }
        if cli.dry_run {
            continue;
        }
        match item.image_json_data {
            SourceValue::String(b64_data) => {
                let image_bytes = BASE64_STANDARD.decode(b64_data)?;
                BufWriter::new(File::create(file_name)?).write_all(&image_bytes)?;
            }
            SourceValue::StringArray(arr) => {
                if item.image_type != ImageType::Svg {
                    bail!("Expected binary data.".red())
                }
                let svg_data = String::from_iter(arr.iter().map(|e| e.as_str()));
                let mut buf = BufWriter::new(File::create(file_name)?);
                buf.write_all(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")?;
                buf.write_all(svg_data.as_bytes())?;
            }
            // just ignore the json type data
            SourceValue::JsonData(_) => {}
        }
    }

    Ok(())
}
fn make_write_message(cli: &cli::Cli, file_name: &Path) {
    if cli.dry_run {
        println!("Would write to {}", file_name.display());
    } else {
        println!("Writing to {}", file_name.display());
    }
}
static LABEL: &str = "label:";

pub fn get_comment_label(source: &str) -> Vec<&str> {
    let mut comments = Vec::new();
    for line in source.lines() {
        let trim_line = line.trim();
        if !trim_line.starts_with('#') {
            continue;
        }
        if let Some((_, identifier)) = trim_line.split_once(LABEL) {
            comments.push(identifier.trim())
        }
    }

    comments
}

fn get_image_candidate(cell: &CodeCell, tag_prefix: &str) -> Option<String> {
    get_image_candidate_comment(cell)
        .or_else(|| get_image_candidate_tags(&cell.metadata.tags, tag_prefix))
}
fn get_image_candidate_comment(cell: &CodeCell) -> Option<String> {
    if let Some(sa) = cell.source.to_string_array() {
        let label = sa.iter().flat_map(|&s| get_comment_label(s)).next();
        label.map(|s| s.to_string())
    } else {
        None
    }
}
fn get_image_candidate_tags<S: AsRef<str>>(
    tags: &Option<Vec<S>>,
    tag_prefix: &str,
) -> Option<String> {
    if let Some(tags) = tags {
        let candidates: Vec<_> = tags
            .iter()
            .filter_map(|t| t.as_ref().strip_prefix(tag_prefix))
            .map(|s| s.trim_start_matches(TO_TRIM))
            .collect();
        if candidates.len() > 1 {
            eprintln!("Warning: Multiple tag candidates: {candidates:?}")
        }
        candidates.first().map(|s| (*s).to_owned())
    } else {
        None
    }
}
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ImageType {
    Gif,
    Jpg,
    Png,
    Webp,
    Svg,
}
impl ImageType {
    fn get_extension(self) -> &'static str {
        use ImageType::*;
        match self {
            Gif => "gif",
            Jpg => "jpg",
            Png => "png",
            Webp => "webp",
            Svg => "svg",
        }
    }
}
fn get_image_type(mime: &str) -> Option<ImageType> {
    use ImageType::*;
    match mime {
        "image/png" => Some(Png),
        "image/jpeg" => Some(Jpg),
        "image/gif" => Some(Gif),
        "image/webp" => Some(Webp),
        "image/svg+xml" => Some(Svg),
        _ => None,
    }
}

fn get_image_data(data: &MimeBundle) -> Vec<(ImageType, &SourceValue)> {
    let mut out = Vec::new();
    for (mime, val) in data {
        if let Some(image_type) = get_image_type(mime) {
            // don't push the json data here so we don't have to process it later
            if !matches!(val, SourceValue::JsonData(_)) {
                out.push((image_type, val));
            }
        }
    }
    out
}
fn checked_create_dir<P: AsRef<Path>>(
    path: P,
    exist_action: NonEmptyDirAction,
    dry_run: bool,
) -> anyhow::Result<()> {
    use NonEmptyDirAction::*;
    let path = path.as_ref();
    if !path.exists() || exist_action == Proceed {
        if !dry_run {
            create_dir_all(path)?;
        }

        return Ok(());
    }
    if path.read_dir()?.next().is_none() {
        Ok(())
    } else if exist_action == Error {
        bail!("Target folder is not empty!".red());
    } else {
        if dry_run {
            eprintln!("Would delete files in directory");
        } else {
            eprintln!("Deleting files in directory");
        }
        if !dry_run {
            remove_dir_all(path)?;
            create_dir_all(path)?;
        }
        Ok(())
    }
}
