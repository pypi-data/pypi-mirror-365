# setup.py
from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        
        # Only show install message if not in quiet mode
        if not any(arg in sys.argv for arg in ['-q', '--quiet', '--silent']):
            self._show_install_message()

    def _show_install_message(self):
        """Show a welcome message after installation"""
        try:
            # Import our color detection
            import platform
            
            def _supports_color_simple():
                """Simplified color detection for install hook"""
                if os.getenv('NO_COLOR'):
                    return False
                if os.getenv('FORCE_COLOR'):
                    return True
                if platform.system() == 'Windows':
                    return os.getenv('WT_SESSION') or os.getenv('ConEmuPID') or os.getenv('CMDER_ROOT')
                return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
            
            # Simple color class for install message
            if _supports_color_simple():
                GREEN = '\033[92m'
                CYAN = '\033[96m'
                YELLOW = '\033[93m'
                BOLD = '\033[1m'
                RESET = '\033[0m'
            else:
                GREEN = CYAN = YELLOW = BOLD = RESET = ''
            
            install_message = f"""
{BOLD}{GREEN}🎉 Successfully installed jaganathanj package!{RESET}

{CYAN}Quick start:{RESET}
  {BOLD}jaganathanj{RESET}        - Show help and available commands
  {BOLD}jaganathanj about{RESET}  - Learn my story
  {BOLD}jaganathanj resume{RESET} - View my professional summary

{YELLOW}You can also import in Python:{RESET}
  {BOLD}import jaganathanj{RESET}
  {BOLD}jaganathanj.about(){RESET}

{GREEN}Thanks for pip installing me! 🚀{RESET}
"""
            print(install_message)
            
        except Exception:
            # Fallback message without colors
            print("\n🎉 jaganathanj package installed successfully!")
            print("Run 'jaganathanj' to get started!")

# Read version from package
def get_version():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'jaganathanj', '__init__.py')) as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except:
        pass
    return '1.0.10'

# Read README for long description
def get_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Personal portfolio and CLI identity package for Jaganathan J"

setup(
    name="jaganathanj",
    version=get_version(),
    description="Personal portfolio and CLI identity package for Jaganathan J, instead of countless resumes",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Jaganathan J",
    author_email="jaganathanjjds@gmail.com",
    url="https://jaganathan-j-portfolio.vercel.app/",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'jaganathanj=jaganathanj.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=["resume", "portfolio", "personal-brand", "cv", "developer", "student"],
    project_urls={
        "Homepage": "https://jaganathan-j-portfolio.vercel.app/",
        "Repository": "https://github.com/J-Jaganathan/jaganathanj-package",
        "Issues": "https://github.com/J-Jaganathan/jaganathanj-package/issues",
        "LinkedIn": "https://linkedin.com/in/jaganathan-j-a5466a257",
        "YouTube": "https://youtube.com/@Tech_CrafterX",
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)