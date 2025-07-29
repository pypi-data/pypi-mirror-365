import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from urllib.parse import urlparse, parse_qs
import socket
import ssl
import datetime
from bs4 import BeautifulSoup
import threading
import re
import os
from PIL import Image, ImageTk
import sys

class AdvancedVulnerabilityScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Scanner")
        self.root.geometry("470x500")
        self.root.configure(bg='#f0f0f0')
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 9))
        self.style.configure('TButton', font=('Arial', 9))
        self.style.configure('Treeview', font=('Arial', 9), rowheight=25)
        
        # Main UI components
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=5, fill=tk.X)
        icon_label = None

        # Try to load and display the icon next to the text
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((24, 24), Image.LANCZOS)
                self.tk_icon = ImageTk.PhotoImage(img)
                icon_label = ttk.Label(header_frame, image=self.tk_icon)
                icon_label.pack(side=tk.LEFT, padx=(0, 8))
        except Exception:
            pass  # Ignore if PIL is not available or icon can't be loaded

        ttk.Label(header_frame, text="Scanner", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Input section
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=5, fill=tk.X, padx=10)
        
        ttk.Label(input_frame, text="Target URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(input_frame, width=40)
        self.url_entry.grid(row=0, column=1, padx=5)
        self.url_entry.insert(0, "https://")
        
        self.scan_btn = ttk.Button(input_frame, text="Start Scan", command=self.start_scan)
        self.scan_btn.grid(row=0, column=2, padx=5)
        
        # Scan options
        options_frame = ttk.LabelFrame(self.root, text="Scan Options", padding=10)
        options_frame.pack(pady=5, fill=tk.X, padx=10)
        
        self.sql_var = tk.BooleanVar(value=True)
        self.xss_var = tk.BooleanVar(value=True)
        self.headers_var = tk.BooleanVar(value=True)
        self.ssl_var = tk.BooleanVar(value=True)
        self.crawl_var = tk.BooleanVar(value=True)
        self.csrf_var = tk.BooleanVar(value=True)
        self.dir_trav_var = tk.BooleanVar(value=True)
        self.cmdi_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="SQL Injection", variable=self.sql_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="XSS", variable=self.xss_var).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Headers", variable=self.headers_var).grid(row=0, column=2, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="SSL/TLS", variable=self.ssl_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="CSRF", variable=self.csrf_var).grid(row=1, column=1, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Directory Traversal", variable=self.dir_trav_var).grid(row=1, column=2, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Command Injection", variable=self.cmdi_var).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Crawl Pages", variable=self.crawl_var).grid(row=2, column=1, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(pady=5, fill=tk.X, padx=10)
        self.status = ttk.Label(self.root, text="Ready to scan")
        self.status.pack()
        
        # Results display
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=5, fill=tk.BOTH, expand=True, padx=10)
        
        # Vulnerabilities tab
        vuln_frame = ttk.Frame(notebook)
        self.results_tree = ttk.Treeview(vuln_frame, columns=('severity', 'type', 'details'), show='headings')
        self.results_tree.heading('severity', text='Severity')
        self.results_tree.heading('type', text='Vulnerability')
        self.results_tree.heading('details', text='Details')
        self.results_tree.column('severity', width=80, anchor=tk.CENTER)
        self.results_tree.column('type', width=120)
        self.results_tree.column('details', width=400)
        
        scrollbar = ttk.Scrollbar(vuln_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        notebook.add(vuln_frame, text='Vulnerabilities')
        
        # Details tab
        details_frame = ttk.Frame(notebook)
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=('Consolas', 9))
        self.details_text.pack(fill=tk.BOTH, expand=True)
        notebook.add(details_frame, text='Details')
        
        # Configure tags for severity colors
        self.results_tree.tag_configure('high', background='#ffcccc')
        self.results_tree.tag_configure('medium', background='#fff3cd')
        self.results_tree.tag_configure('low', background='#d4edda')
        self.results_tree.tag_configure('info', background='#d1ecf1')
    
    def start_scan(self):
        url = self.url_entry.get().strip()
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "URL must start with http:// or https://")
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.details_text.delete(1.0, tk.END)
        
        self.scan_btn.config(state=tk.DISABLED)
        
        scan_thread = threading.Thread(target=self.run_scan, args=(url,), daemon=True)
        scan_thread.start()
    
    def run_scan(self, url):
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            base_url = f"{parsed_url.scheme}://{domain}"
            
            # Calculate total steps for progress
            total_steps = sum([
                self.sql_var.get(),
                self.xss_var.get(),
                self.headers_var.get(),
                self.ssl_var.get(),
                self.csrf_var.get(),
                self.dir_trav_var.get(),
                self.cmdi_var.get(),
                self.crawl_var.get()
            ])
            current_step = 0
            
            # SSL/TLS Check
            if self.ssl_var.get():
                self.update_status("Checking SSL/TLS configuration...")
                self.check_ssl(domain)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # Headers Analysis
            if self.headers_var.get():
                self.update_status("Analyzing HTTP headers...")
                self.analyze_headers(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # SQL Injection Test
            if self.sql_var.get():
                self.update_status("Testing for SQL Injection...")
                self.test_sql_injection(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # XSS Test
            if self.xss_var.get():
                self.update_status("Testing for XSS vulnerabilities...")
                self.test_xss(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # CSRF Test
            if self.csrf_var.get():
                self.update_status("Checking for CSRF vulnerabilities...")
                self.test_csrf(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # Directory Traversal Test
            if self.dir_trav_var.get():
                self.update_status("Testing for Directory Traversal...")
                self.test_directory_traversal(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # Command Injection Test
            if self.cmdi_var.get():
                self.update_status("Testing for Command Injection...")
                self.test_command_injection(url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            # Crawl Pages
            if self.crawl_var.get():
                self.update_status("Crawling website for links...")
                self.crawl_pages(base_url)
                current_step += 1
                self.update_progress(current_step, total_steps)
            
            self.update_status("Scan completed successfully!")
            messagebox.showinfo("Scan Complete", "Vulnerability scan completed!")
        
        except Exception as e:
            self.add_result("High", "Scan Error", f"Error during scan: {str(e)}")
            self.update_status(f"Error: {str(e)}")
        
        finally:
            self.scan_btn.config(state=tk.NORMAL)
    
    def update_status(self, message):
        self.status.config(text=message)
        self.root.update()
    
    def update_progress(self, current, total):
        progress = (current / total) * 100
        self.progress['value'] = progress
        self.root.update()
    
    def add_result(self, severity, vuln_type, details):
        tag = severity.lower()
        self.results_tree.insert('', tk.END, values=(severity, vuln_type, details), tags=(tag,))
        self.details_text.insert(tk.END, f"[{severity}] {vuln_type}: {details}\n\n")
        self.details_text.see(tk.END)
        self.root.update()
    
    def check_ssl(self, domain):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
            
            # Check certificate expiration
            expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_remaining = (expiry_date - datetime.datetime.now()).days
            
            details = f"SSL Certificate:\nIssuer: {cert['issuer'][1][0][1]}\n"
            details += f"Valid Until: {cert['notAfter']} ({days_remaining} days remaining)\n"
            
            # Check for weak protocols
            weak_protocols = self.detect_weak_ssl_protocols(domain)
            if weak_protocols:
                details += f"Weak Protocols: {', '.join(weak_protocols)}\n"
                self.add_result("High", "Weak SSL Protocols", f"Server supports: {', '.join(weak_protocols)}")
            
            if days_remaining < 30:
                self.add_result("High", "SSL Expiry", f"Certificate expires in {days_remaining} days")
            elif days_remaining < 90:
                self.add_result("Medium", "SSL Expiry", f"Certificate expires in {days_remaining} days")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("High", "SSL Error", f"SSL verification failed: {str(e)}")
    
    def detect_weak_ssl_protocols(self, domain):
        weak_protocols = []
        protocols = {
            'SSLv2': ssl.PROTOCOL_SSLv2,
            'SSLv3': ssl.PROTOCOL_SSLv3,
            'TLSv1': ssl.PROTOCOL_TLSv1,
            'TLSv1.1': ssl.PROTOCOL_TLSv1_1
        }
        
        for name, proto in protocols.items():
            try:
                context = ssl.SSLContext(proto)
                with socket.create_connection((domain, 443)) as sock:
                    with context.wrap_socket(sock, server_hostname=domain):
                        weak_protocols.append(name)
            except:
                continue
        
        return weak_protocols
    
    def analyze_headers(self, url):
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            details = "Security Headers Analysis:\n"
            missing_headers = []
            security_headers = {
                'X-XSS-Protection': '1; mode=block',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'Content-Security-Policy': '',
                'Strict-Transport-Security': '',
                'Referrer-Policy': 'no-referrer'
            }
            
            for header, expected in security_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif expected and isinstance(expected, list) and headers[header] not in expected:
                    self.add_result("Medium", f"Misconfigured {header}", 
                                  f"Expected one of {expected}, got {headers[header]}")
                elif expected and isinstance(expected, str) and headers[header] != expected:
                    self.add_result("Medium", f"Misconfigured {header}", 
                                  f"Expected {expected}, got {headers[header]}")
            
            if missing_headers:
                self.add_result("Medium", "Missing Security Headers", 
                              f"Missing: {', '.join(missing_headers)}")
            
            # Check for server information disclosure
            if 'server' in headers:
                self.add_result("Low", "Server Disclosure", f"Server header: {headers['server']}")
            
            # Check for CORS misconfiguration
            if 'access-control-allow-origin' in headers and headers['access-control-allow-origin'] == '*':
                self.add_result("Medium", "Permissive CORS", "Access-Control-Allow-Origin is set to '*'")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "Headers Error", f"Header analysis failed: {str(e)}")
    
    def test_sql_injection(self, url):
        payloads = [
            "'", "\"", "' OR '1'='1", "' OR 1=1--", 
            "' OR 1=1#", "' OR 1=1/*", "' UNION SELECT null,version()--"
        ]
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if not params:
                self.add_result("Info", "SQLi Test", "No parameters to test")
                return
            
            vulnerable = False
            details = "SQL Injection Tests:\n"
            
            for param in params:
                for payload in payloads:
                    test_url = url.replace(f"{param}={params[param][0]}", f"{param}={payload}")
                    try:
                        response = requests.get(test_url, timeout=5)
                        if self.detect_sql_errors(response.text):
                            vulnerable = True
                            details += f"Potential SQLi in {param} with payload: {payload}\n"
                            break
                    except:
                        continue
            
            if vulnerable:
                self.add_result("High", "SQL Injection", "Potential SQLi vulnerabilities detected")
            else:
                self.add_result("Low", "SQL Injection", "No obvious SQLi vulnerabilities found")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "SQLi Error", f"SQLi test failed: {str(e)}")
    
    def detect_sql_errors(self, content):
        errors = [
            "SQL syntax", "MySQL server", "ORA-", "syntax error",
            "unclosed quotation mark", "Microsoft OLE DB Provider",
            "ODBC Driver", "PostgreSQL", "SQLite", "MariaDB"
        ]
        return any(error.lower() in content.lower() for error in errors)
    
    def test_xss(self, url):
        payloads = [
            "<script>alert(1)</script>", 
            "<img src=x onerror=alert(1)>",
            "\"><script>alert(1)</script>",
            "javascript:alert(1)",
            "onmouseover=alert(1)"
        ]
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if not params:
                self.add_result("Info", "XSS Test", "No parameters to test")
                return
            
            vulnerable = False
            details = "XSS Tests:\n"
            
            for param in params:
                for payload in payloads:
                    test_url = url.replace(f"{param}={params[param][0]}", f"{param}={payload}")
                    try:
                        response = requests.get(test_url, timeout=5)
                        if payload in response.text:
                            vulnerable = True
                            details += f"Potential XSS in {param} with payload: {payload}\n"
                            break
                    except:
                        continue
            
            if vulnerable:
                self.add_result("High", "XSS", "Potential XSS vulnerabilities detected")
            else:
                self.add_result("Low", "XSS", "No obvious XSS vulnerabilities found")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "XSS Error", f"XSS test failed: {str(e)}")
    
    def test_csrf(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')
            
            vulnerable = False
            details = "CSRF Tests:\n"
            
            for form in forms:
                if not form.find('input', {'name': 'csrf_token'}) and \
                   not form.find('input', {'name': 'csrfmiddlewaretoken'}):
                    vulnerable = True
                    details += "Form without CSRF token found\n"
                    break
            
            if vulnerable:
                self.add_result("Medium", "CSRF", "Forms without CSRF protection detected")
            else:
                self.add_result("Low", "CSRF", "No obvious CSRF vulnerabilities found")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "CSRF Error", f"CSRF test failed: {str(e)}")
    
    def test_directory_traversal(self, url):
        payloads = [
            "../../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "....//....//etc/passwd"
        ]
        
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            paths = [p for p in parsed.path.split('/') if p]
            
            vulnerable = False
            details = "Directory Traversal Tests:\n"
            
            for payload in payloads:
                test_url = f"{base_url}/{payload}"
                try:
                    response = requests.get(test_url, timeout=5)
                    if "root:" in response.text or "bin:" in response.text:
                        vulnerable = True
                        details += f"Potential directory traversal with payload: {payload}\n"
                        break
                except:
                    continue
            
            if vulnerable:
                self.add_result("High", "Directory Traversal", "Potential directory traversal vulnerabilities detected")
            else:
                self.add_result("Low", "Directory Traversal", "No obvious directory traversal vulnerabilities found")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "Dir Traversal Error", f"Directory traversal test failed: {str(e)}")
    
    def test_command_injection(self, url):
        payloads = [
            ";id", "|id", "`id`", "$(id)", 
            "|| ping -c 1 localhost", "&& ping -c 1 localhost"
        ]
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            if not params:
                self.add_result("Info", "Command Injection", "No parameters to test")
                return
            
            vulnerable = False
            details = "Command Injection Tests:\n"
            
            for param in params:
                for payload in payloads:
                    test_url = url.replace(f"{param}={params[param][0]}", f"{param}={params[param][0]}{payload}")
                    try:
                        response = requests.get(test_url, timeout=5)
                        if "uid=" in response.text or "bytes from" in response.text:
                            vulnerable = True
                            details += f"Potential command injection in {param} with payload: {payload}\n"
                            break
                    except:
                        continue
            
            if vulnerable:
                self.add_result("High", "Command Injection", "Potential command injection vulnerabilities detected")
            else:
                self.add_result("Low", "Command Injection", "No obvious command injection vulnerabilities found")
            
            self.details_text.insert(tk.END, details + "\n")
        
        except Exception as e:
            self.add_result("Medium", "CMD Injection Error", f"Command injection test failed: {str(e)}")
    
    def crawl_pages(self, base_url):
        try:
            visited = set()
            to_visit = {base_url}
            max_pages = 5  # Limit for demo
            
            details = "Crawling Results:\n"
            
            while to_visit and len(visited) < max_pages:
                url = to_visit.pop()
                if url in visited:
                    continue
                
                try:
                    response = requests.get(url, timeout=5)
                    visited.add(url)
                    details += f"Found: {url}\n"
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('http') and base_url in href and href not in visited:
                            to_visit.add(href)
                        elif href.startswith('/'):
                            absolute = base_url + href
                            if absolute not in visited:
                                to_visit.add(absolute)
                    
                    # Check for forms
                    forms = soup.find_all('form')
                    if forms:
                        details += f"Found {len(forms)} forms on {url}\n"
                    
                    self.root.update()
                except:
                    continue
            
            details += f"\nCrawled {len(visited)} pages\n"
            self.details_text.insert(tk.END, details + "\n")
            
            if len(visited) >= max_pages:
                self.add_result("Info", "Crawl Limit", f"Limited to {max_pages} pages for demo")
        
        except Exception as e:
            self.add_result("Medium", "Crawl Error", f"Crawling failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        
    app = AdvancedVulnerabilityScanner(root)
    root.mainloop()
    
def run_gui():
    root = tk.Tk()
    app = AdvancedVulnerabilityScanner(root)
    root.mainloop()