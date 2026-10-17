import { Outlet, useLocation } from "react-router-dom";

import Sidebar from "@/components/layout/Sidebar";
import TopBar from "@/components/layout/TopBar";

// Layout principal: la sidebar de filtros solo aparece en el dashboard.
export default function AppShell() {
  const { pathname } = useLocation();
  const showSidebar = pathname === "/";

  return (
    <div className="min-h-screen">
      <TopBar />
      <div className={`grid min-h-[calc(100vh-56px)] ${showSidebar ? "grid-cols-[270px_1fr]" : "grid-cols-1"}`}>
        {showSidebar && <Sidebar />}
        <main className="overflow-x-auto p-[18px_22px]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
