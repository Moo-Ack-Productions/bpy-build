use std::{collections::HashMap, path::PathBuf};
use clap::Parser;
use serde::{Serialize, Deserialize};

/// Arguments for bpy-build
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to file
    #[arg(short, long)]
    path: Option<PathBuf>,
}

/// Configuration found in bpy-build.yaml
#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct BpyBuildConf {
    /// The path to the addon folder
    addon_folder: String,
    /// The name of the built zip
    build_name: String,
    /// The versions/paths to install the 
    /// built addon to
    install_versions: Vec<String>,
    /// Actions to perform during the build
    during_build: HashMap<String, Vec<String>>,
}

fn main() -> Result<(), serde_yaml::Error> {
    let args = Args::parse();

    let config: BpyBuildConf = match args.path {
        Some(path) => {
            let file = std::fs::read_to_string(path).expect("File not found !");
            println!("{}", file);
            serde_yaml::from_str(&file).unwrap()
        }
        None => {
            let file = std::fs::read_to_string("./bpy-build.yaml").expect("File not found !");
            println!("{}", file);
            serde_yaml::from_str(&file).unwrap()
        }
    };
    println!("{:?}", config);
    Ok(())
}
