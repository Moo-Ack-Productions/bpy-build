use std::{collections::HashMap, path::PathBuf};
use clap::{Parser, ValueHint, Command, CommandFactory};
use clap_complete::{Shell, Generator, generate};
use serde::{Serialize, Deserialize};

/// Arguments for bpy-build
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to file
    #[arg(short, long, value_hint = ValueHint::FilePath)]
    path: Option<PathBuf>,
    
    /// Creates shell completion script
    #[arg(long = "generate", value_enum)]
    generator: Option<Shell>,
}


/// Create completion script
fn print_completions<G: Generator>(gen: G, cmd: &mut Command) {
    generate(gen, cmd, cmd.get_name().to_string(), &mut std::io::stdout());
}

/// Configuration found in bpy-build.yaml
#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct BpyBuildConf {
    /// The path to the addon folder
    addon_folder: PathBuf,
    /// The name of the built zip
    build_name: String,
    /// The versions/paths to install the 
    /// built addon to
    install_versions: Option<Vec<String>>,
    /// Actions to perform during the build
    during_build: Option<HashMap<String, Vec<String>>>,
}

fn main() -> Result<(), serde_yaml::Error> {
    let args = Args::parse();
    if let Some(shell) = args.generator {
        print_completions(shell, &mut Args::command())
    } else {
        // Parse the contents of bpy-build.yaml
        let config: BpyBuildConf = serde_yaml::from_str(
            &match args.path {
                Some(path) => {
                    std::fs::read_to_string(path)
                        .expect("File not found !")
                }
                None => {
                    std::fs::read_to_string("./bpy-build.yaml")
                        .expect("File not found !")
                }
            }
        ).unwrap();

        // Make sure the addon folder actually exists
        if !config.addon_folder.exists() {
            println!("Addon folder {} does not exist!", config.addon_folder.to_str().unwrap());
        }
        
        // Get and make a build directory, with 
        // an addon_build folder (to maintain a
        // proper structure in the zip file)
        let build_dir = std::env::current_dir().unwrap()
            .join(PathBuf::from("build"));
        let addon_build = build_dir
            .join(PathBuf::from("addon_build"));
        if !addon_build.exists() {
            std::fs::create_dir_all(addon_build).unwrap();
        }
    }
    Ok(())
}
