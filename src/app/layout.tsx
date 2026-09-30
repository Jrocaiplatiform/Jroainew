import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "J-ROC AI — Build Your Own AI Company",
  description: "J-ROC AI is the AI operating system for builders, businesses, creators and enterprise teams.",
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <div className="public-shell">
    <header className="public-nav">
      <Link href="/" className="public-brand">J-ROC <span>AI</span></Link>
      <nav>
        <Link href="/platform">Platform</Link>
        <Link href="/solutions">Solutions</Link>
        <Link href="/marketplace">Marketplace</Link>
        <Link href="/academy">Academy</Link><Link href="/entertainment">Entertainment Studio</Link>
        <Link href="/enterprise">Enterprise</Link>
        <Link href="/resources">Resources</Link>
      </nav>
      <div className="nav-actions"><Link href="/login" className="nav-contact">SIGN IN</Link><Link href="/chairman/login" className="chairman-login">CHAIRMAN LOGIN</Link></div>
    </header>
    <main>{children}</main>
    <footer className="public-footer">
      <div className="footer-brand"><strong>J-ROC <span>AI</span></strong><p>Build Your Own AI Company.</p></div>
      <div><b>Platform</b><Link href="/platform">Platform</Link><Link href="/solutions">Solutions</Link><Link href="/marketplace">Marketplace</Link><Link href="/academy">Academy</Link></div>
      <div><b>Company</b><Link href="/company/about">About</Link><Link href="/company/manifesto">Manifesto</Link><Link href="/contact">Contact</Link><Link href="/resources/trust">Trust & Security</Link></div>
      <div><b>Access</b><Link href="/login">Customer Workspace</Link><Link href="/chairman/login">Chairman Login</Link></div>
      <div className="footer-bottom">© 2026 J-ROC AI. The public site is the front door. The operating system stays behind authorized access.</div>
    </footer>
  </div>;
}