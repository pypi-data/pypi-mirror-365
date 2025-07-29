use crate::cli::args::InitArgs;
use anstream::println;
use owo_colors::OwoColorize;
use std::env;
use std::io::{Read, Write};

fn get_init_script_content() -> String {
    let exe_path = env::current_exe()
        .expect("Could not get current executable path")
        .display()
        .to_string();
    let script = format!(
        r#"
# Generated initialization script for virtual environment
function __meowda_exe() {{
    {exe_path} "$@"
}}

function __meowda_hashr() {{
    if [ -n "${{ZSH_VERSION:+x}}" ]; then
        rehash
    elif [ -n "${{POSH_VERSION:+x}}" ]; then
        :  # pass
    else
        hash -r
    fi
}}

function __meowda_activate() {{
    local venv_base=$({exe_path} env dir)
    local venv_name=$2
    local venv_path="$venv_base/$venv_name"
    if [ -d "$venv_path" ]; then
        source "$venv_path/bin/activate"
        echo "Activated virtual environment: $venv_path"
    else
        echo "Virtual environment not found: $venv_path"
    fi
}}

function __meowda_deactivate() {{
    deactivate
    echo "Deactivated virtual environment."
}}

function meowda() {{
    local cmd="${{1-__missing__}}"
    case "$cmd" in
        (activate) __meowda_activate "$@" ;;
        (deactivate) __meowda_deactivate ;;
        (*) __meowda_exe "$@" ;;
    esac
    __meowda_hashr
}}
"#,
    );
    script
}

fn inject_init_script(shell_profile: &str) {
    // Append the initialization script to the shell profile
    let meowda_init_comment = "Meowda initialization script";
    let init_script = format!(
        r#"
# {meowda_init_comment}
MEOWDA_TMP_SCRIPT="/tmp/meowda-init-tmp.sh"
meowda generate-init-script > "$MEOWDA_TMP_SCRIPT"
source "$MEOWDA_TMP_SCRIPT"
rm -f "$MEOWDA_TMP_SCRIPT"
"#
    );
    let mut file = std::fs::OpenOptions::new()
        .append(true)
        .create(true)
        .read(true)
        .open(shell_profile)
        .expect("Failed to open shell profile");

    let mut buf = String::new();
    file.read_to_string(&mut buf)
        .expect("Failed to read shell profile");

    if buf.contains(meowda_init_comment) {
        println!(
            "{}",
            format!("Initialization script already exists in {shell_profile}. Skipping injection.")
                .yellow()
        );
    } else {
        file.write_all(init_script.as_bytes())
            .expect("Failed to write initialization script to shell profile");
    }
}

pub async fn generate_init_script() {
    let script_content = get_init_script_content();
    println!("{}", script_content);
}

pub async fn init(args: InitArgs) {
    inject_init_script(args.shell_profile.as_str());
}
