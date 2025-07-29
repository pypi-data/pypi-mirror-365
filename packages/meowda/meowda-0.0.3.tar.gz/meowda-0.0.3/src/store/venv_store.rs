/// Provides a user-level directory for storing application state.
/// Heavy inspiration from the uv implementation.
use crate::envs::EnvVars;
use crate::store::file_lock::FileLock;
use etcetera::BaseStrategy;
use std::io::{self, Write};
use std::path::PathBuf;

/// Returns an appropriate user-level directory for storing application state.
///
/// Corresponds to `$XDG_DATA_HOME/meowda` on Unix.
fn user_state_dir() -> Option<PathBuf> {
    etcetera::base_strategy::choose_base_strategy()
        .ok()
        .map(|dirs| dirs.data_dir().join("meowda"))
}

pub struct VenvStore {
    path: PathBuf,
}

impl VenvStore {
    /// Detects the appropriate directory for storing virtual environments.
    ///
    /// Prefer, in order:
    ///
    /// 1. The specific tool directory specified by the user, i.e., `MEOWDA_VENV_DIR`
    /// 2. A directory in the system-appropriate user-level data directory, e.g., `~/.local/meowda/venvs`
    /// 3. A directory in the local data directory, e.g., `./.meowda/venvs`
    fn detect_path() -> PathBuf {
        if let Some(tool_dir) = std::env::var_os(EnvVars::MEOWDA_VENV_DIR).filter(|s| !s.is_empty())
        {
            let tool_dir_clone = tool_dir.clone();
            std::path::absolute(tool_dir)
                .unwrap_or_else(|_| panic!("Invalid path for MEOWDA_VENV_DIR: {tool_dir_clone:?}"))
        } else {
            let meowda_store = user_state_dir().unwrap_or_else(|| PathBuf::from(".meowda"));
            meowda_store.join("venvs")
        }
    }

    pub fn new() -> Self {
        let path = Self::detect_path();

        VenvStore { path }
    }

    pub fn is_ready(&self) -> bool {
        self.path.exists() && self.path.is_dir() && self.path.join(".gitignore").exists()
    }

    pub fn init(&self) -> io::Result<()> {
        std::fs::create_dir_all(&self.path)?;

        // Add a .gitignore.
        match std::fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(self.path.join(".gitignore"))
        {
            Ok(mut file) => file.write_all(b"*"),
            Err(err) if err.kind() == io::ErrorKind::AlreadyExists => Ok(()),
            Err(err) => Err(err),
        }
    }

    pub fn path(&self) -> &PathBuf {
        &self.path
    }

    pub fn exists(&self, name: &str) -> bool {
        self.path.join(name).exists()
    }

    pub async fn lock(&self) -> FileLock {
        let lock_path = self.path.join(".lock");
        // FileLockGuard::new(lock_path)
        FileLock::acquire(lock_path, "venv_store")
            .await
            .expect("Failed to acquire lock for VenvStore")
    }
}
