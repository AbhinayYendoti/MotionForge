export function Footer() {
  return (
    <footer className="mt-24 rounded-t-[40px] bg-footer px-6 py-16 text-footer-foreground md:px-12 md:pb-32">
      <div className="mx-auto max-w-page">
        <h2 className="display-lg max-w-2xl text-footer-foreground">We are here when your campaign needs motion.</h2>
        <div className="mt-16 grid gap-10 border-t border-footer-foreground/20 pt-12 md:grid-cols-4">
          {[
            ["Need help?", "Support", "Render status", "Contact"],
            ["Product", "Pipeline", "Storyboard", "Renderer"],
            ["Company", "Security", "Reliability", "Deploy"],
            ["Resources", "Docs", "API", "System status"]
          ].map(([title, ...links]) => (
            <div key={title}>
              <p className="mb-5 text-[13px] font-[700] uppercase leading-none tracking-[0.04em] text-footer-foreground/60">{title}</p>
              <ul className="space-y-3 text-[14px] font-[450] leading-[1.4] text-footer-foreground">
                {links.map((link) => (
                  <li key={link}>
                    <a href="#" className="focus-ring rounded-xs">
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-16 flex flex-col gap-6 border-t border-footer-foreground/20 pt-8 text-[13px] font-[450] text-footer-foreground/70 md:flex-row md:items-center md:justify-between">
          <p>Copyright 2026 MotionForge. All rights reserved.</p>
          <button className="focus-ring w-fit rounded-pill border border-footer-foreground/40 px-5 py-3 text-footer-foreground">United States / English</button>
        </div>
      </div>
    </footer>
  );
}
