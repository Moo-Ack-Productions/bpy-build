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
    addon_folder: String,
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
    }
    Ok(())
}
