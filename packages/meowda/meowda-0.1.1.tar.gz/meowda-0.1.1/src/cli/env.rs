use crate::backend::{EnvInfo, VenvBackend};
use crate::cli::args::{CreateArgs, DirArgs, ListArgs, RemoveArgs};
use crate::store::venv_store::VenvScope;
use anstream::println;
use anyhow::Result;
use owo_colors::OwoColorize;

pub async fn create(args: CreateArgs, backend: &VenvBackend) -> Result<()> {
    let scope = crate::cli::utils::parse_scope(&args.scope)?;
    backend
        .create(&args.name, &args.python, args.clear, scope)
        .await?;
    println!("Virtual environment '{}' created successfully.", args.name);
    Ok(())
}

pub async fn remove(args: RemoveArgs, backend: &VenvBackend) -> Result<()> {
    let scope = crate::cli::utils::parse_scope(&args.scope)?;
    let detected_venv_scope = crate::cli::utils::search_venv(scope, &args.name)?;
    backend
        .remove(&args.name, Some(detected_venv_scope))
        .await?;
    println!("Virtual environment '{}' removed successfully.", args.name);
    Ok(())
}

fn show_envs(envs: &[EnvInfo], scope: &VenvScope, shadowed_names: &[String]) -> Result<()> {
    let scope_name = match scope {
        VenvScope::Local => "local",
        VenvScope::Global => "global",
    };
    if envs.is_empty() {
        println!("No {scope_name} virtual environments found.");
    } else {
        println!("Available {scope_name} virtual environments:");
        for env in envs {
            let indicator = if env.is_active { "* " } else { "  " };
            let mut name_display = format!("{}{}", indicator, env.name);
            let mut info_display = env.path.display().blue().to_string();
            if shadowed_names.contains(&env.name) && !env.is_active {
                name_display = name_display.dimmed().to_string();
            }
            if env.is_active {
                name_display = name_display.green().bold().to_string();
            }
            if let Some(config) = &env.config
                && let Some(version) = &config.version
            {
                info_display = format!(
                    "{} {}",
                    info_display,
                    format!("python {version}").cyan().bold()
                );
            }
            println!("{} ({})", name_display, info_display);
        }
    }
    Ok(())
}

pub async fn list(args: ListArgs, backend: &VenvBackend) -> Result<()> {
    let (local_envs, global_envs) = backend.list().await?;
    let scope = crate::cli::utils::parse_scope(&args.scope)?;
    let mut shadowed_names = vec![];
    if scope.is_none() || scope == Some(VenvScope::Local) {
        show_envs(&local_envs, &VenvScope::Local, &[])?;
        shadowed_names.extend(local_envs.iter().map(|env| env.name.clone()));
    }
    if scope.is_none() || scope == Some(VenvScope::Global) {
        show_envs(&global_envs, &VenvScope::Global, &shadowed_names)?;
    }
    Ok(())
}

pub async fn dir(args: DirArgs, backend: &VenvBackend) -> Result<()> {
    let scope = crate::cli::utils::parse_scope(&args.scope)?;
    let path = backend.dir(scope)?;
    println!("{}", path.display());
    Ok(())
}
