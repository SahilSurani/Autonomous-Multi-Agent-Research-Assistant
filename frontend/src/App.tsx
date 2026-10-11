import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ResearchConsole } from './components/ResearchConsole';
import { MemoryBank } from './components/MemoryBank';
import { PdfChat } from './components/PdfChat';
import { SettingsModal } from './components/SettingsModal';
import { fetchSettings } from './api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'research' | 'memory' | 'pdf' | 'settings'>('research');
  const [workspaces, setWorkspaces] = useState<string[]>(['default']);
  const [currentWorkspace, setCurrentWorkspace] = useState<string>('default');
  const [backendOnline, setBackendOnline] = useState(false);
  const [isResearchRunning, setIsResearchRunning] = useState(false);

  // Load workspaces from backend on mount
  useEffect(() => {
    fetchSettings()
      .then((s) => {
        setWorkspaces(s.available_workspaces || ['default']);
        setBackendOnline(true);
      })
      .catch(() => setBackendOnline(false));
  }, []);

  return (
    <div className="flex min-h-screen bg-[#060a13] text-slate-100 antialiased selection:bg-indigo-500/40 selection:text-white">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        workspaces={workspaces}
        currentWorkspace={currentWorkspace}
        setCurrentWorkspace={setCurrentWorkspace}
        backendOnline={backendOnline}
        isResearchRunning={isResearchRunning}
      />

      <main className="flex-1 overflow-y-auto max-h-screen">
        <div className="p-6 lg:p-10 max-w-[1400px] mx-auto">
          <div className={activeTab === 'research' ? 'block' : 'hidden'}>
            <ResearchConsole
              currentWorkspace={currentWorkspace}
              onExecutingChange={setIsResearchRunning}
            />
          </div>
          <div className={activeTab === 'memory' ? 'block' : 'hidden'}>
            <MemoryBank currentWorkspace={currentWorkspace} />
          </div>
          <div className={activeTab === 'pdf' ? 'block' : 'hidden'}>
            <PdfChat currentWorkspace={currentWorkspace} />
          </div>
          <div className={activeTab === 'settings' ? 'block' : 'hidden'}>
            <SettingsModal />
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
