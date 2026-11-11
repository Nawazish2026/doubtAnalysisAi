// Public browser configuration for the live faculty console.
// Values are injected from the FRONTEND Vercel project's Environment Variables.
// Never add DATABASE_URL, service-role keys, or JWT signing secrets here.
module.exports = function handler(_req, res) {
  const config = {
    apiBaseUrl: process.env.ACADZA_API_BASE_URL || process.env.API_BASE_URL || "",
    supabaseUrl: process.env.SUPABASE_URL || "",
    supabasePublishableKey:
      process.env.SUPABASE_PUBLISHABLE_KEY || process.env.SUPABASE_ANON_KEY || "",
  };

  const missing = Object.entries(config)
    .filter(([, value]) => !value)
    .map(([key]) => key);

  res.setHeader("Content-Type", "application/javascript; charset=utf-8");
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).send(
    "window.ACADZA_CONFIG = Object.freeze(" +
      JSON.stringify(config) +
      ");\nwindow.ACADZA_CONFIG_STATUS = " +
      JSON.stringify({ configured: missing.length === 0, missing }) +
      ";\n"
  );
};
