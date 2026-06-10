function PageShell({ children }) {
  return (
    <main className="mx-auto max-w-7xl px-4 pb-10 pt-6 sm:px-6 lg:px-8">
      <div className="space-y-8">{children}</div>
    </main>
  );
}

export default PageShell;
