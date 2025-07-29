# jaganathanj/__init__.py
"""
Jaganathan J - Personal Brand as a Python Package
==================================================

A unique way to share my professional story, achievements, and contact information.
Because why settle for a boring resume when you can pip install a person details?

Usage:
    import jaganathanj
    jaganathanj.about()     # Detailed story and background
    jaganathanj.resume()    # Quick resume summary
    jaganathanj.cv()        # Full detailed CV
    jaganathanj.contact()   # All contact information
    jaganathanj.linkedin()  # Open LinkedIn profile
"""

import webbrowser
import sys
import os
import platform
from typing import NoReturn

__version__ = "1.0.10"
__author__ = "Jaganathan J"
__email__ = "jaganathanjjds@gmail.com"

# Auto-detect color support
def _supports_color():
    """
    Detect if the terminal supports ANSI color codes.
    Returns True if colors are supported, False otherwise.
    """
    # Check environment variables first
    if os.getenv('NO_COLOR'):
        return False
    
    if os.getenv('FORCE_COLOR'):
        return True
    
    # Check if we're in a known terminal that supports colors
    term = os.getenv('TERM', '').lower()
    colorterm = os.getenv('COLORTERM', '').lower()
    
    if colorterm in ('truecolor', '24bit'):
        return True
    
    if term in ('xterm', 'xterm-color', 'xterm-256color', 'screen', 'screen-256color', 'tmux', 'tmux-256color'):
        return True
    
    # Windows-specific checks
    if platform.system() == 'Windows':
        # Windows Terminal and modern terminals support ANSI
        if os.getenv('WT_SESSION'):  # Windows Terminal
            return True
        
        # Check for ConEmu, cmder, etc.
        if os.getenv('ConEmuPID') or os.getenv('CMDER_ROOT'):
            return True
        
        # For Windows 10+ with ANSI support enabled
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                if mode.value & 0x0004:
                    return True
                # Try to enable it
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                return True
        except:
            pass
        
        # Default to False for older Windows CMD
        return False
    
    # For Unix-like systems, check if stdout is a TTY
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

# Initialize color support
_COLOR_SUPPORTED = _supports_color()

# Terminal colors and formatting
class Colors:
    if _COLOR_SUPPORTED:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    else:
        # No color fallback
        HEADER = ''
        OKBLUE = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''

def _print_colored(text: str, color: str = Colors.ENDC) -> None:
    """Print text with color formatting"""
    print(f"{color}{text}{Colors.ENDC}")

def _should_show_welcome():
    """
    Determine if we should show the welcome message.
    Only show on CLI usage, not on import.
    """
    # Check if we're being run as a CLI command
    if len(sys.argv) > 0:
        script_name = os.path.basename(sys.argv[0])
        if script_name in ('jaganathanj', '__main__.py') or sys.argv[0].endswith('jaganathanj'):
            return True
    
    # Check if this is a direct CLI invocation
    if __name__ == '__main__' or getattr(sys, '_called_from_test', False):
        return True
        
    return False

def _welcome_message() -> None:
    """Display welcome message when package is used as CLI"""
    welcome_text = f"""
{Colors.BOLD}{Colors.HEADER}================================================================================
                    🚀 WELCOME TO JAGANATHANJ PACKAGE 🚀
================================================================================{Colors.ENDC}

{Colors.OKGREEN}Hey there! You just imported a person as a Python package. Cool, right?{Colors.ENDC}

{Colors.OKCYAN}Available commands:{Colors.ENDC}
  {Colors.BOLD}jaganathanj about{Colors.ENDC}     - My detailed story and journey
  {Colors.BOLD}jaganathanj resume{Colors.ENDC}    - Quick professional summary
  {Colors.BOLD}jaganathanj cv{Colors.ENDC}        - Full detailed curriculum vitae
  {Colors.BOLD}jaganathanj contact{Colors.ENDC}   - All my contact information
  {Colors.BOLD}jaganathanj linkedin{Colors.ENDC}  - Open my LinkedIn profile

{Colors.WARNING}Prerequisites: Python 3.6+, terminal with basic ASCII support{Colors.ENDC}

{Colors.OKBLUE}Start with jaganathanj about to learn my story!{Colors.ENDC}

{Colors.HEADER}================================================================================{Colors.ENDC}
"""
    print(welcome_text)

def about() -> None:
    """Display detailed about me story"""
    about_text = """================================================================================
                            JAGANATHAN J - ABOUT ME
================================================================================

Prerequisites: Python 3.6+, terminal with basic ASCII support, no additional packages required.

Hey there! You just imported me as a Python package. That's not normal, and neither am I.

Most people put their story on LinkedIn. I built mine into code you can pip install.
Why? Because everything I do reflects how I think differently about problems.

--------------------------------------------------------------------------------
At the time of creating this package, I'm in my final year of Computer Science and 
Engineering at SRM Easwari Engineering College, Chennai, with a CGPA of 8.89/10. 
I've served as the class representative for three consecutive semesters — a role I 
stepped into after volunteering and was entrusted with by faculty. It's been a space 
where I learned to lead through clarity, coordination, and calm, especially when things 
got complex.

This isn't just another student story. This is about someone who sees patterns where
others see chaos, and builds solutions where others see obstacles.

THE TURNING POINT:
The weekend before the Computer Networks exam? 60+ classmates panicking about
12 Cisco Packet Tracer experiments they couldn't grasp. RIP protocols, DHCP configs,
static routing - technical nightmares that make or break your semester.

I had one week. I self-mastered every single experiment. Then I did something that
defined who I am: I called a 6-hour Google Meet session. Real-time doubt clearing.
Live problem-solving. No slides, just pure technical knowledge transfer.

Result? 100% pass rate. Every single person passed the next day.

That's when I realized - my superpower isn't just solving problems. It's scaling
solutions to lift entire communities.

BEYOND THE CLASSROOM:
I don't just code. I patent ideas. Filed "202441089112 A" for a SARIMA-based GPS
alternative using machine learning time series prediction. When GPS fails, temporal
mapping takes over. Infrastructure independence through intelligent prediction.

I don't just learn. I teach. My YouTube channel "Tech CrafterX" hit 667%_ subscriber
growth in 15 days. Created 33-minute cloud computing tutorials that 150+ students
across multiple sections now use. Not because I'm chasing fame - because knowledge
should elevate everyone.

I don't just build projects. I build experiences. Architected a real-time Firebase
note taking app as the sole developer among 60 students. While others built Udemy clones,
I delivered a live demo where the entire class interacted with disappearing messages
in real-time. Perfect score. Faculty recognition. Production deployment.

SCALING ORDER:  
During my 6th semester, I noticed that our mini-project documentation was fragmented 
and unclear. So, I redesigned it — structure, formatting, clarity — and proposed a cleaner 
format. It was approved by every project guide and adopted across the department. 
Hundreds of students and faculty now use it — a simple change that saved hours of 
collective confusion.


THE DAILY GRIND:
Do I solve coding problems regularly? Absolutely. Sometimes it's LeetCode. Other 
times it's system design, data structures, or whatever sparks my curiosity that week. 
The topics and intensity vary — but the habit stays.

I don't follow a strict #100DaysOfCode routine. For me, problem-solving is less about 
streaks and more about staying mentally sharp, building real intuition, and applying 
what I learn in meaningful ways.

THE FIRST SPARK:  
It started early. In 6th grade, I built a racing robot from scratch using a 12V battery, 
IR sensors, motors, and more — and won my first competition. That experience wired 
something permanent into me: the thrill of building, solving, and improving. I've been 
chasing better systems ever since.

BEYOND CODE:  
I've been committed to fitness since 6th grade — building physical strength as a 
foundation for mental resilience. You need both when you're debugging at 2 AM or guiding 
70 classmates through TCP/IP right before an exam with no margin for error.

Setbacks? I've had them. A gaming addiction during school nearly knocked me off course. 
But I turned that phase into fuel for a comeback. Through focus and discipline, 
I scored 191/200 in my Higher Secondary exams and topped my school in Mathematics with 99%.

College came with its own challenges — but I stayed sharp. I stepped up when it mattered 
most: teaching 12 full-scale networking experiments via Google Meet to over 60 students 
before an exam, all while managing my own prep. No spotlight. No formal credit. Just impact.

Every stumble has been a step forward. Growth, for me, has always been intentional — 
mentally, physically, and technically.

--------------------------------------------------------------------------------

NPTEL Gold Medal in Cloud Computing (90% with 2 days prep). 
IIT Madras Shaastra 2025 Hackathon Finalist.
MongoDB Certified Student Developer.
Winner of Pitch Perfect Competition.

I make time for high-leverage growth, even under pressure.

But here's what matters more than certificates:

When professors face cryptic errors in legacy C programs, they reach out to me.  
When classmates can't rely on the manual or faculty, they rely on my explanation.  
When precision and last-minute fixes are the only option — I show up.  

This isn't about being the smartest person in the room. It's about being the person
who makes everyone else smarter.

MY VISION:
I'm not just looking for a job. I'm building a career in LLM, Data Science, AI/ML 
Engineering, or Full-Stack Development where I can create scalable impact. Where my 
obsession with understanding systems deeply can solve real problems for real people.

I want to work with teams that appreciate someone who learns fast, teaches others,
and sees opportunities where others see obstacles. Someone who files patents, builds
viral educational content, and turns academic crises into learning victories.

CONTACT & CONNECT:
Main Email: jaganathanjjds@gmail.com
College Email: 310622104064@eec.srmrmp.edu.in
GitHub: https://github.com/J-Jaganathan
LinkedIn: https://linkedin.com/in/jaganathan-j-a5466a257
YouTube: https://youtube.com/@Tech_CrafterX
Portfolio: https://jaganathan-j-portfolio.vercel.app/

Even this format - packaging myself as importable code - reflects how I approach
everything. Unconventional, functional, and memorable.

Because in a world full of identical resumes, why not be the one they can literally
import and run?

Welcome to my story. Thanks for pip installing me.

- Jaganathan J

================================================================================"""
    
    _print_colored(about_text, Colors.OKCYAN)

def resume() -> None:
    """Display quick resume summary"""
    resume_text = f"""
{Colors.BOLD}{Colors.HEADER}================================================================================
                        JAGANATHAN J - RESUME SUMMARY
================================================================================{Colors.ENDC}

{Colors.BOLD}🎓 EDUCATION{Colors.ENDC}
   B.Tech Computer Science & Engineering | SRM Easwari Engineering College
   CGPA: 8.89/10 | Expected Graduation: June 2026
   Class Representative (3 consecutive semesters)

{Colors.BOLD}💼 EXPERIENCE{Colors.ENDC}
   • 📺 Content Creator & Technical Instructor – YouTube (Tech_CrafterX)
     → Produced AWS and Cloud Computing tutorials with 667% subscriber growth in 15 days  
     → Reached 500+ views and 150+ student adoption across multiple sections

   • 🧠 Data Science Intern – Personifwy (Nov–Dec 2024, Remote)  
     → Developed machine learning models and conducted statistical analysis using Python  
     → Improved prediction accuracy by 15% through feature tuning and cross-validation

   • 🧬 Data Science Intern – Adverk Technologies (June–July 2023, Remote)  
     → Gained early exposure to biomedical ML by working on stroke and breast cancer prediction models  
     → Contributed to model optimization and preprocessing pipelines in a healthcare-focused dataset  
     → Built foundational intuition in applying supervised learning to real-world medical risk assessments

   • 🧑‍🏫 Technical Mentor – Computer Networks Lab  
     → Trained 70+ students on Cisco Packet Tracer experiments before exam week  
     → Led real-time sessions that resulted in a 100% pass rate across sections

{Colors.BOLD}🚀 KEY PROJECTS{Colors.ENDC}
   • Real-time Chat Application (Firebase, JavaScript) - Perfect score, sole developer
   • Network Communication System (Java, Socket Programming) - Custom laptop-to-laptop protocol
   • Voice-Controlled Notes App (JavaScript, Web Speech API) - 95% accuracy
   • Patent Filed: GPS Alternative using SARIMA Model (App. No. 202441089112 A)

{Colors.BOLD}🏆 ACHIEVEMENTS{Colors.ENDC}
   • IIT Madras Shaastra 2025 Hackathon Finalist
   • NPTEL Gold Medal - Cloud Computing (90%)
   • MongoDB Certified Student Developer
   • Winner - Pitch Perfect Competition

{Colors.BOLD}💻 TECH STACK{Colors.ENDC}
   Languages: Python, Java, JavaScript, C++, HTML/CSS
   Cloud: AWS, Firebase, MongoDB, SQL
   Tools: VS Code, GitHub, Android Studio
   Specialties: Machine Learning, NLP, System Architecture

{Colors.BOLD}📬 CONTACT{Colors.ENDC}
   Email: jaganathanjjds@gmail.com
   Portfolio: https://jaganathan-j-portfolio.vercel.app/
   
{Colors.OKGREEN}Run jaganathanj.about() for the full story!{Colors.ENDC}

{Colors.HEADER}================================================================================{Colors.ENDC}
"""
    print(resume_text)

def cv() -> None:
    """Display full detailed CV"""
    cv_text = f"""
{Colors.BOLD}{Colors.HEADER}================================================================================
                     JAGANATHAN J - CURRICULUM VITAE
================================================================================{Colors.ENDC}

{Colors.BOLD}PERSONAL INFORMATION{Colors.ENDC}
Name: Jaganathan Jothi Narayanan
Email: jaganathanjjds@gmail.com
LinkedIn: https://linkedin.com/in/jaganathan-j-a5466a257
GitHub: https://github.com/J-Jaganathan
YouTube: https://youtube.com/@Tech_CrafterX
Portfolio: https://jaganathan-j-portfolio.vercel.app/

{Colors.BOLD}EXECUTIVE SUMMARY{Colors.ENDC}
Self-directed computer science engineer with patent-pending innovation, 500+ educational
video views, and a track record of 100% peer success rates in critical technical
interventions. Demonstrated ability to master complex systems independently, scale
educational impact across 150+ students, and build production-ready applications.

{Colors.BOLD}EDUCATION{Colors.ENDC}
Bachelor of Engineering - Computer Science & Engineering (2022-2026)
SRM Easwari Engineering College, Chennai
CGPA: 8.89/10
• Class Representative (3 consecutive semesters)
• Patent Application Filed: GPS Alternative System (App. No. 202441089112 A)
• Perfect Academic Record: Zero failures from grades 1-12

{Colors.BOLD}PROFESSIONAL EXPERIENCE{Colors.ENDC}

Content Creator & Technical Instructor (Sep 2024 – Present)
YouTube Channel - Tech CrafterX | Remote
• Achieved 667% subscriber growth in 15 days with 500+ views through AWS tutorials
• Produced 3+ comprehensive tutorials on Cloud Computing and Hadoop
• Created content adopted by 150+ students across multiple sections

Data Science Intern (Nov 2024 – Dec 2024)
Personifwy | Remote, Bengaluru
• Applied Python, ML, and statistical analysis to real-world projects
• Improved model accuracy by 15% through advanced preprocessing techniques

Technical Mentor (Nov 2024)
Computer Networks Lab, SRM Easwari Engineering College
• Conducted intensive crisis session for 70+ students before critical exam
• Achieved 100% class pass rate through real-time doubt clearing sessions

Data Science Intern (Jun 2023 – Jul 2023)
Adverk Technologies | Remote, Bengaluru
• Built foundational ML pipelines for Breast Cancer and Stroke Prediction
• Explored data preprocessing and binary classification using health datasets

{Colors.BOLD}TECHNICAL PROJECTS{Colors.ENDC}

Grocery Helper Application | Firebase, JavaScript, HTML/CSS
• Architected real-time note-taking system as sole developer among 60 students
• Implemented disappearing messages with cross-browser compatibility
• Achieved perfect score with faculty recognition

Network Communication System | Java, ServerSocket Programming
• Built custom laptop-to-laptop communication protocol
• Self-taught Java through independent learning for project requirements
• Demonstrated advanced networking concepts at undergraduate level

Voice-Controlled Notes Application | Java, Web Speech API
• Developed hands-free note-taking app with 95% voice-to-text accuracy
• Implemented accessibility features for enhanced user experience

NLP Expression Evaluator | Prolog
• Built intelligent text parser for arithmetic expressions
• Supports natural language input with calculated results

{Colors.BOLD}RESEARCH & INTELLECTUAL PROPERTY{Colors.ENDC}
Patent Application - Temporal Mapping Technology (Nov 2024)
Application No.: 202441089112 A
• Developed SARIMA-based GPS alternative using ML time-series prediction
• Addresses critical infrastructure dependency in location services
• Prototype development in progress for backup navigation systems

{Colors.BOLD}CERTIFICATIONS & ACHIEVEMENTS{Colors.ENDC}
• NPTEL Cloud Computing: 90% (Gold Medal) - 2024
• NPTEL Industry 4.0 & IIoT: 80% (Silver Medal) - 2023
• MongoDB Student Developer Course - Certified (Jul 2024)
• Winner - Pitch Perfect Competition (Nov 2023)
• Finalist - IIT Madras Shaastra 2025 Hackathon (Jan 2025)

{Colors.BOLD}TECHNICAL EXPERTISE{Colors.ENDC}
Programming Languages: Python, Java, JavaScript, C++, HTML/CSS, C, MATLAB
Cloud & Databases: AWS, Firebase, MongoDB, MySQL
Development Tools: Git, VS Code, Android Studio, Cisco Packet Tracer
Data Science: NumPy, Pandas, Matplotlib, Scikit-learn
Network Protocols: TCP/IP, RIP, OSPF, DHCP, Static/Dynamic Routing
Specialties: Machine Learning, NLP, System Architecture, Socket Programming

{Colors.BOLD}LEADERSHIP & IMPACT{Colors.ENDC}
• Educational Impact: 150+ students using created tutorials
• Crisis Management: 100% exam pass rate intervention
• Process Innovation: Created department-wide documentation template
• Community Building: Consistent technical mentorship and knowledge sharing

{Colors.BOLD}PERSONAL DEVELOPMENT{Colors.ENDC}
• Physical Fitness: Regular strength training since 6th grade
• Problem Solving: Daily competitive programming practice (1.25+ hours average)
• Growth Mindset: Transformed setbacks into systematic self-improvement
• Quality Focus: Perfectionist approach to technical work and documentation

{Colors.HEADER}================================================================================{Colors.ENDC}
"""
    print(cv_text)

def contact() -> None:
    """Display all contact information"""
    contact_text = f"""
{Colors.BOLD}{Colors.HEADER}================================================================================
                       JAGANATHAN J - CONTACT INFORMATION
================================================================================{Colors.ENDC}

{Colors.BOLD}{Colors.OKGREEN}📧 EMAIL{Colors.ENDC}
   jaganathanjjds@gmail.com

{Colors.BOLD}{Colors.OKBLUE}🌐 PROFESSIONAL PROFILES{Colors.ENDC}
   LinkedIn: https://linkedin.com/in/jaganathan-j-a5466a257
   GitHub: https://github.com/J-Jaganathan
   Portfolio: https://jaganathan-j-portfolio.vercel.app/

{Colors.BOLD}{Colors.WARNING}📺 CONTENT & EDUCATION{Colors.ENDC}
   YouTube: https://youtube.com/@Tech_CrafterX
   Channel Focus: Cloud Computing, Data Science tutorials

{Colors.BOLD}{Colors.OKCYAN}💼 AVAILABILITY{Colors.ENDC}
   Status: Final year B.Tech student (Graduating June 2026)
   Seeking: Full-time roles, internships, research collaborations
   Interests: Data Science, AI/ML Engineering, Full-Stack Development

{Colors.BOLD}{Colors.OKGREEN}🎯 WHAT I'M LOOKING FOR{Colors.ENDC}
   • Teams that value rapid learning and knowledge sharing
   • Projects involving scalable system architecture
   • Opportunities to create educational and social impact
   • Roles where I can solve complex technical challenges

{Colors.BOLD}{Colors.HEADER}Response Time: Usually within 24 hours{Colors.ENDC}

{Colors.OKBLUE}Feel free to reach out for collaborations, opportunities, or just to chat about tech!{Colors.ENDC}

{Colors.HEADER}================================================================================{Colors.ENDC}
"""
    print(contact_text)

def linkedin() -> None:
    """Open LinkedIn profile in browser"""
    linkedin_url = "https://linkedin.com/in/jaganathan-j-a5466a257"
    try:
        webbrowser.open(linkedin_url)
        _print_colored(f"\n🌐 Opening LinkedIn profile: {linkedin_url}", Colors.OKGREEN)
        _print_colored("If the browser didn't open automatically, copy the URL above.", Colors.WARNING)
    except Exception as e:
        _print_colored(f"❌ Could not open browser. Please visit: {linkedin_url}", Colors.FAIL)

def github() -> None:
    """Open GitHub profile in browser"""
    github_url = "https://github.com/J-Jaganathan"
    try:
        webbrowser.open(github_url)
        _print_colored(f"\n🐙 Opening GitHub profile: {github_url}", Colors.OKGREEN)
        _print_colored("Check out my repositories and contributions!", Colors.OKCYAN)
    except Exception as e:
        _print_colored(f"❌ Could not open browser. Please visit: {github_url}", Colors.FAIL)

def portfolio() -> None:
    """Open portfolio website in browser"""
    portfolio_url = "https://jaganathan-j-portfolio.vercel.app/"
    try:
        webbrowser.open(portfolio_url)
        _print_colored(f"\n💼 Opening portfolio: {portfolio_url}", Colors.OKGREEN)
        _print_colored("Explore my projects and achievements!", Colors.OKCYAN)
    except Exception as e:
        _print_colored(f"❌ Could not open browser. Please visit: {portfolio_url}", Colors.FAIL)

def youtube() -> None:
    """Open YouTube channel in browser"""
    youtube_url = "https://youtube.com/@Tech_CrafterX"
    try:
        webbrowser.open(youtube_url)
        _print_colored(f"\n📺 Opening YouTube channel: {youtube_url}", Colors.OKGREEN)
        _print_colored("Subscribe for AWS, Cloud Computing, and Data Science tutorials!", Colors.WARNING)
    except Exception as e:
        _print_colored(f"❌ Could not open browser. Please visit: {youtube_url}", Colors.FAIL)

def help() -> None:
    """Display help information"""
    help_text = f"""
{Colors.BOLD}{Colors.HEADER}================================================================================
                         JAGANATHANJ PACKAGE - HELP
================================================================================{Colors.ENDC}

{Colors.BOLD}{Colors.OKGREEN}AVAILABLE COMMANDS:{Colors.ENDC}

{Colors.BOLD}📖 Information Commands:{Colors.ENDC}
   jaganathanj.about()     - Detailed personal story and journey
   jaganathanj.resume()    - Quick professional summary
   jaganathanj.cv()        - Full detailed curriculum vitae
   jaganathanj.contact()   - Complete contact information

{Colors.BOLD}🌐 Link Commands:{Colors.ENDC}
   jaganathanj.linkedin()  - Open LinkedIn profile in browser
   jaganathanj.github()    - Open GitHub profile in browser
   jaganathanj.portfolio() - Open portfolio website in browser
   jaganathanj.youtube()   - Open YouTube channel in browser

{Colors.BOLD}ℹ️  Utility Commands:{Colors.ENDC}
   jaganathanj.help()      - Show this help message

{Colors.BOLD}{Colors.OKCYAN}PACKAGE INFO:{Colors.ENDC}
   Version: {__version__}
   Author: {__author__}
   Email: {__email__}

{Colors.BOLD}{Colors.WARNING}GETTING STARTED:{Colors.ENDC}
   Start with jaganathanj.about() to learn my complete story!

{Colors.HEADER}================================================================================{Colors.ENDC}
"""
    print(help_text)

# Only show welcome message when used as CLI, not on import
# This will be handled by the CLI module instead

# Make functions available at package level
__all__ = [
    'about', 'resume', 'cv', 'contact', 'linkedin', 
    'github', 'portfolio', 'youtube', 'help'
]