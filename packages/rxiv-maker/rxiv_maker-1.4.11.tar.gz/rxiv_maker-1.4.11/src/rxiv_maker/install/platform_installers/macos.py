"""macOS-specific system dependency installer."""

import subprocess
import urllib.request
from pathlib import Path

from ..utils.logging import InstallLogger
from ..utils.progress import ProgressIndicator


class MacOSInstaller:
    """macOS-specific installer for rxiv-maker dependencies."""

    def __init__(self, logger: InstallLogger, progress: ProgressIndicator):
        """Initialize macOS installer.

        Args:
            logger: Logger instance
            progress: Progress indicator instance
        """
        self.logger = logger
        self.progress = progress
        self.temp_dir = Path.home() / "Downloads" / "rxiv-maker-temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Detect architecture
        self.is_apple_silicon = self._is_apple_silicon()

    def _is_apple_silicon(self) -> bool:
        """Check if running on Apple Silicon."""
        try:
            result = subprocess.run(
                ["uname", "-m"], capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() == "arm64"
        except:
            return False

    def install_system_libraries(self) -> bool:
        """Install system libraries required by Python packages."""
        self.logger.info("Installing system libraries on macOS...")

        # Install Cairo and Pango for CairoSVG (Mermaid diagram conversion)
        cairo_success = self._install_cairo_libraries()

        # On macOS, most system libraries are handled by pip wheels
        # We may need to install some build tools for certain packages

        try:
            # Check if we can import key packages
            import matplotlib
            import numpy
            import PIL

            self.logger.success("System libraries already available")
            return cairo_success
        except ImportError as e:
            self.logger.warning(f"Some system libraries may be missing: {e}")

            # Try to install Xcode command line tools
            return self._install_xcode_tools() and cairo_success

    def install_latex(self) -> bool:
        """Install LaTeX distribution on macOS."""
        self.logger.info("Installing LaTeX on macOS...")

        # Check if LaTeX is already installed
        if self._is_latex_installed():
            self.logger.success("LaTeX already installed")
            return True

        # Try different installation methods
        methods = [self._install_latex_homebrew, self._install_latex_direct]

        for method in methods:
            try:
                if method():
                    self._install_latex_packages()
                    return True
            except Exception as e:
                self.logger.debug(f"LaTeX installation method failed: {e}")
                continue

        self.logger.error("Failed to install LaTeX using any method")
        return False

    def install_nodejs(self) -> bool:
        """Install Node.js and npm packages on macOS."""
        self.logger.info("Installing Node.js on macOS...")

        # Check if Node.js is already installed
        if self._is_nodejs_installed():
            self.logger.success("Node.js already installed")
            return self._install_npm_packages()

        # Try different installation methods
        methods = [self._install_nodejs_homebrew, self._install_nodejs_direct]

        for method in methods:
            try:
                if method():
                    return self._install_npm_packages()
            except Exception as e:
                self.logger.debug(f"Node.js installation method failed: {e}")
                continue

        self.logger.error("Failed to install Node.js using any method")
        return False

    def install_r(self) -> bool:
        """Install R language on macOS."""
        self.logger.info("Installing R on macOS...")

        # Check if R is already installed
        if self._is_r_installed():
            self.logger.success("R already installed")
            return True

        # Try different installation methods
        methods = [self._install_r_homebrew, self._install_r_direct]

        for method in methods:
            try:
                if method():
                    return True
            except Exception as e:
                self.logger.debug(f"R installation method failed: {e}")
                continue

        self.logger.error("Failed to install R using any method")
        return False

    def _is_latex_installed(self) -> bool:
        """Check if LaTeX is installed."""
        try:
            result = subprocess.run(
                ["pdflatex", "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            return result.returncode == 0
        except:
            return False

    def _is_nodejs_installed(self) -> bool:
        """Check if Node.js is installed."""
        try:
            node_result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            npm_result = subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            return node_result.returncode == 0 and npm_result.returncode == 0
        except:
            return False

    def _is_r_installed(self) -> bool:
        """Check if R is installed."""
        try:
            result = subprocess.run(
                ["R", "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            return result.returncode == 0
        except:
            return False

    def _is_homebrew_installed(self) -> bool:
        """Check if Homebrew is installed."""
        try:
            result = subprocess.run(
                ["brew", "--version"], capture_output=True, timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def _install_xcode_tools(self) -> bool:
        """Install Xcode command line tools."""
        self.logger.info("Installing Xcode command line tools...")

        try:
            # Check if already installed
            result = subprocess.run(
                ["xcode-select", "-p"], capture_output=True, timeout=10
            )

            if result.returncode == 0:
                self.logger.success("Xcode command line tools already installed")
                return True

            # Try to install
            result = subprocess.run(
                ["xcode-select", "--install"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.logger.success("Xcode command line tools installed")
                return True
            else:
                self.logger.debug(f"Xcode tools install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Error installing Xcode tools: {e}")
            return False

    def _install_homebrew(self) -> bool:
        """Install Homebrew package manager."""
        self.logger.info("Installing Homebrew...")

        try:
            # Download and run install script
            install_script = "curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
            result = subprocess.run(
                ["bash", "-c", install_script],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("Homebrew installed")

                # Add to PATH
                self._add_homebrew_to_path()
                return True
            else:
                self.logger.debug(f"Homebrew install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Error installing Homebrew: {e}")
            return False

    def _add_homebrew_to_path(self):
        """Add Homebrew to PATH in shell profiles."""
        if self.is_apple_silicon:
            homebrew_path = "/opt/homebrew/bin"
        else:
            homebrew_path = "/usr/local/bin"

        # Add to common shell profiles
        shell_profiles = [
            Path.home() / ".zshrc",
            Path.home() / ".bash_profile",
            Path.home() / ".bashrc",
        ]

        for profile in shell_profiles:
            if profile.exists():
                try:
                    content = profile.read_text()
                    if homebrew_path not in content:
                        with profile.open("a") as f:
                            f.write(f'\\nexport PATH="{homebrew_path}:$PATH"\\n')
                        self.logger.debug(f"Added Homebrew to PATH in {profile}")
                except Exception as e:
                    self.logger.debug(f"Error updating {profile}: {e}")

    def _install_cairo_libraries(self) -> bool:
        """Install Cairo and Pango libraries for CairoSVG."""
        self.logger.info(
            "Installing Cairo and Pango libraries for Mermaid diagram conversion..."
        )

        # Install Homebrew if not available
        if not self._is_homebrew_installed() and not self._install_homebrew():
            self.logger.warning("Cannot install Cairo libraries without Homebrew")
            return False

        try:
            # Install Cairo and Pango via Homebrew
            packages = ["cairo", "pango", "pkg-config"]
            for package in packages:
                result = subprocess.run(
                    ["brew", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode != 0:
                    self.logger.debug(f"Failed to install {package}: {result.stderr}")
                    # Continue with other packages even if one fails
                    continue
                else:
                    self.logger.debug(f"Successfully installed {package}")

            # Configure environment variables for CairoSVG
            self._configure_cairo_environment()

            self.logger.success("Cairo and Pango libraries installed using Homebrew")
            return True
        except Exception as e:
            self.logger.debug(f"Cairo installation failed: {e}")
            self.logger.warning(
                "Failed to install Cairo libraries. CairoSVG may not work properly."
            )
            return False

    def _configure_cairo_environment(self):
        """Configure environment variables for Cairo library discovery."""
        homebrew_prefix = "/opt/homebrew" if self.is_apple_silicon else "/usr/local"

        # Set up environment variables for CairoSVG
        env_vars = {
            "PKG_CONFIG_PATH": f"{homebrew_prefix}/lib/pkgconfig:{homebrew_prefix}/share/pkgconfig",
            "DYLD_LIBRARY_PATH": f"{homebrew_prefix}/lib",
            "CAIRO_LIBRARY_PATH": f"{homebrew_prefix}/lib",
        }

        # Add to shell profiles
        shell_profiles = [
            Path.home() / ".zshrc",
            Path.home() / ".bash_profile",
            Path.home() / ".bashrc",
        ]

        env_lines = []
        for var, value in env_vars.items():
            env_lines.append(f'export {var}="{value}:${var}"')

        for profile in shell_profiles:
            if profile.exists():
                try:
                    content = profile.read_text()
                    # Check if Cairo environment is already configured
                    if "PKG_CONFIG_PATH" in content and homebrew_prefix in content:
                        continue

                    with profile.open("a") as f:
                        f.write(
                            "\n# Cairo/CairoSVG environment variables for Rxiv-Maker\n"
                        )
                        for line in env_lines:
                            f.write(f"{line}\n")
                        f.write("\n")
                    self.logger.debug(f"Added Cairo environment variables to {profile}")
                except Exception as e:
                    self.logger.debug(f"Error updating {profile}: {e}")

        # Set environment variables for current session
        import os

        for var, value in env_vars.items():
            current_value = os.environ.get(var, "")
            if current_value:
                os.environ[var] = f"{value}:{current_value}"
            else:
                os.environ[var] = value
            self.logger.debug(f"Set {var}={os.environ[var]}")

        self.logger.debug("Configured Cairo environment variables for CairoSVG")

    def _install_latex_homebrew(self) -> bool:
        """Install LaTeX using Homebrew."""
        self.logger.info("Trying to install LaTeX using Homebrew...")

        # Install Homebrew if not available
        if not self._is_homebrew_installed() and not self._install_homebrew():
            return False

        try:
            # Install BasicTeX (smaller than full MacTeX)
            result = subprocess.run(
                ["brew", "install", "--cask", "basictex"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("LaTeX installed using Homebrew")
                # Add LaTeX to PATH
                self._add_latex_to_path()
                return True
            else:
                self.logger.debug(f"Homebrew install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Error installing LaTeX with Homebrew: {e}")
            return False

    def _install_latex_direct(self) -> bool:
        """Install LaTeX using direct download."""
        self.logger.info("Trying to install LaTeX using direct download...")

        try:
            # Download BasicTeX
            if self.is_apple_silicon:
                pkg_url = "https://mirror.ctan.org/systems/mac/mactex/mactex-basictex-20230313.pkg"
            else:
                pkg_url = "https://mirror.ctan.org/systems/mac/mactex/mactex-basictex-20230313.pkg"

            pkg_path = self.temp_dir / "basictex.pkg"

            self.logger.info("Downloading BasicTeX...")
            urllib.request.urlretrieve(pkg_url, pkg_path)

            # Install package
            self.logger.info("Installing BasicTeX...")
            result = subprocess.run(
                ["sudo", "installer", "-pkg", str(pkg_path), "-target", "/"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("LaTeX installed using direct download")
                self._add_latex_to_path()
                return True
            else:
                self.logger.debug(f"Direct install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Direct download failed: {e}")
            return False

    def _add_latex_to_path(self):
        """Add LaTeX to PATH in shell profiles."""
        latex_path = "/Library/TeX/texbin"

        # Add to common shell profiles
        shell_profiles = [
            Path.home() / ".zshrc",
            Path.home() / ".bash_profile",
            Path.home() / ".bashrc",
        ]

        for profile in shell_profiles:
            if profile.exists():
                try:
                    content = profile.read_text()
                    if latex_path not in content:
                        with profile.open("a") as f:
                            f.write(f'\\nexport PATH="{latex_path}:$PATH"\\n')
                        self.logger.debug(f"Added LaTeX to PATH in {profile}")
                except Exception as e:
                    self.logger.debug(f"Error updating {profile}: {e}")

    def _install_nodejs_homebrew(self) -> bool:
        """Install Node.js using Homebrew."""
        self.logger.info("Trying to install Node.js using Homebrew...")

        # Install Homebrew if not available
        if not self._is_homebrew_installed() and not self._install_homebrew():
            return False

        try:
            # Install Node.js
            result = subprocess.run(
                ["brew", "install", "node@18"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("Node.js installed using Homebrew")
                return True
            else:
                self.logger.debug(f"Homebrew install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Error installing Node.js with Homebrew: {e}")
            return False

    def _install_nodejs_direct(self) -> bool:
        """Install Node.js using direct download."""
        self.logger.info("Trying to install Node.js using direct download...")

        try:
            # Download Node.js installer
            if self.is_apple_silicon:
                pkg_url = "https://nodejs.org/dist/v18.17.0/node-v18.17.0.pkg"
            else:
                pkg_url = "https://nodejs.org/dist/v18.17.0/node-v18.17.0.pkg"

            pkg_path = self.temp_dir / "nodejs.pkg"

            self.logger.info("Downloading Node.js...")
            urllib.request.urlretrieve(pkg_url, pkg_path)

            # Install package
            self.logger.info("Installing Node.js...")
            result = subprocess.run(
                ["sudo", "installer", "-pkg", str(pkg_path), "-target", "/"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("Node.js installed using direct download")
                return True
            else:
                self.logger.debug(f"Direct install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Direct download failed: {e}")
            return False

    def _install_r_homebrew(self) -> bool:
        """Install R using Homebrew."""
        self.logger.info("Trying to install R using Homebrew...")

        # Install Homebrew if not available
        if not self._is_homebrew_installed() and not self._install_homebrew():
            return False

        try:
            # Install R
            result = subprocess.run(
                ["brew", "install", "r"], capture_output=True, text=True, timeout=600
            )

            if result.returncode == 0:
                self.logger.success("R installed using Homebrew")
                return True
            else:
                self.logger.debug(f"Homebrew install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Error installing R with Homebrew: {e}")
            return False

    def _install_r_direct(self) -> bool:
        """Install R using direct download."""
        self.logger.info("Trying to install R using direct download...")

        try:
            # Download R installer
            if self.is_apple_silicon:
                pkg_url = "https://cran.r-project.org/bin/macosx/big-sur-arm64/base/R-4.3.1-arm64.pkg"
            else:
                pkg_url = "https://cran.r-project.org/bin/macosx/base/R-4.3.1.pkg"

            pkg_path = self.temp_dir / "r-installer.pkg"

            self.logger.info("Downloading R...")
            urllib.request.urlretrieve(pkg_url, pkg_path)

            # Install package
            self.logger.info("Installing R...")
            result = subprocess.run(
                ["sudo", "installer", "-pkg", str(pkg_path), "-target", "/"],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                self.logger.success("R installed using direct download")
                return True
            else:
                self.logger.debug(f"Direct install failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.debug(f"Direct download failed: {e}")
            return False

    def _install_latex_packages(self) -> bool:
        """Install additional LaTeX packages."""
        self.logger.info("Installing additional LaTeX packages...")

        packages = [
            "latexdiff",
            "biber",
            "biblatex",
            "pgfplots",
            "adjustbox",
            "collectbox",
        ]

        success = True
        for package in packages:
            try:
                self.logger.debug(f"Installing LaTeX package: {package}")
                result = subprocess.run(
                    ["sudo", "tlmgr", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    self.logger.debug(f"Failed to install {package}: {result.stderr}")
                    success = False
            except Exception as e:
                self.logger.debug(f"Error installing {package}: {e}")
                success = False

        return success

    def _install_npm_packages(self) -> bool:
        """Install required npm packages."""
        self.logger.info("No npm packages required - mermaid-cli dependency removed")

        # Mermaid diagrams are now handled via Python-based solutions (cairosvg)
        # No need for puppeteer-based mermaid-cli
        return True
