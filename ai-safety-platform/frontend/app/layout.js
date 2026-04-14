import "../styles/globals.css";

export const metadata = {
  title: "AI Safety & Smart FIR Platform",
  description: "Detect harmful content, protect children, and generate legally structured FIRs.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
