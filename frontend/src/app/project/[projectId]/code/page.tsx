'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { ProjectNav } from '@/components/ProjectNav'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { 
  Folder, 
  FileCode, 
  Search, 
  Download,
  ExternalLink,
  ChevronRight,
  ChevronDown,
  GitBranch
} from 'lucide-react'

export default function CodeExplorerPage() {
  const params = useParams()
  const projectId = params.projectId as string

  const [selectedFile, setSelectedFile] = useState<string | null>('app/page.tsx')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedFolders, setExpandedFolders] = useState<string[]>(['app', 'components'])

  // Mock file tree - will be replaced with real data
  const fileTree = {
    'app': {
      type: 'folder',
      files: {
        'page.tsx': { type: 'file', size: '2.4 KB', language: 'typescript' },
        'layout.tsx': { type: 'file', size: '1.1 KB', language: 'typescript' },
        'globals.css': { type: 'file', size: '800 B', language: 'css' }
      }
    },
    'components': {
      type: 'folder',
      files: {
        'hero.tsx': { type: 'file', size: '3.2 KB', language: 'typescript' },
        'nav.tsx': { type: 'file', size: '1.8 KB', language: 'typescript' },
        'footer.tsx': { type: 'file', size: '1.2 KB', language: 'typescript' }
      }
    },
    'package.json': { type: 'file', size: '500 B', language: 'json' },
    'README.md': { type: 'file', size: '1.5 KB', language: 'markdown' }
  }

  // Mock code content
  const mockCode = `'use client'

import { Hero } from '@/components/hero'
import { Nav } from '@/components/nav'
import { Footer } from '@/components/footer'

export default function Home() {
  return (
    <main className="min-h-screen">
      <Nav />
      <Hero />
      <Footer />
    </main>
  )
}`

  const toggleFolder = (folder: string) => {
    setExpandedFolders(prev =>
      prev.includes(folder)
        ? prev.filter(f => f !== folder)
        : [...prev, folder]
    )
  }

  const getFileIcon = (file: string) => {
    if (file.endsWith('.tsx') || file.endsWith('.ts')) {
      return <FileCode className="h-4 w-4 text-blue-500" />
    } else if (file.endsWith('.css')) {
      return <FileCode className="h-4 w-4 text-pink-500" />
    } else if (file.endsWith('.json')) {
      return <FileCode className="h-4 w-4 text-yellow-500" />
    } else if (file.endsWith('.md')) {
      return <FileCode className="h-4 w-4 text-gray-500" />
    }
    return <FileCode className="h-4 w-4 text-gray-400" />
  }

  const renderFileTree = (tree: any, path = '') => {
    return Object.entries(tree).map(([name, item]: [string, any]) => {
      const fullPath = path ? `${path}/${name}` : name
      
      if (item.type === 'folder') {
        const isExpanded = expandedFolders.includes(name)
        return (
          <div key={fullPath}>
            <button
              onClick={() => toggleFolder(name)}
              className="flex items-center gap-2 w-full px-2 py-1.5 text-sm hover:bg-gray-100 rounded transition-colors"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              <Folder className="h-4 w-4 text-purple-500" />
              <span className="font-medium">{name}</span>
            </button>
            {isExpanded && (
              <div className="ml-6 mt-1 space-y-1">
                {renderFileTree(item.files, fullPath)}
              </div>
            )}
          </div>
        )
      } else {
        return (
          <button
            key={fullPath}
            onClick={() => setSelectedFile(fullPath)}
            className={`flex items-center gap-2 w-full px-2 py-1.5 text-sm hover:bg-gray-100 rounded transition-colors ${
              selectedFile === fullPath ? 'bg-purple-50 text-purple-700' : ''
            }`}
          >
            {getFileIcon(name)}
            <span>{name}</span>
            <span className="ml-auto text-xs text-muted-foreground">{item.size}</span>
          </button>
        )
      }
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <ProjectNav projectId={projectId} projectName="Project" />

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-12rem)]">
          {/* Left Sidebar - File Explorer */}
          <Card className="lg:col-span-1">
            <CardContent className="p-4 space-y-4 h-full flex flex-col">
              <div>
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search files..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>

                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm text-muted-foreground">FILES</h3>
                  <Badge variant="secondary" className="text-xs">
                    12 files
                  </Badge>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto space-y-1">
                {renderFileTree(fileTree)}
              </div>

              <div className="pt-4 border-t space-y-2">
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <Download className="h-4 w-4 mr-2" />
                  Download Project
                </Button>
                <Button variant="outline" size="sm" className="w-full justify-start">
                  <GitBranch className="h-4 w-4 mr-2" />
                  View on GitHub
                  <ExternalLink className="h-3 w-3 ml-auto" />
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Right Side - Code Viewer */}
          <Card className="lg:col-span-3">
            <CardContent className="p-0 h-full flex flex-col">
              {selectedFile ? (
                <>
                  {/* File Header */}
                  <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
                    <div className="flex items-center gap-3">
                      {getFileIcon(selectedFile)}
                      <span className="font-mono text-sm font-semibold">{selectedFile}</span>
                      <Badge variant="secondary">TypeScript</Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm">
                        Copy
                      </Button>
                      <Button variant="ghost" size="sm">
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Code Content */}
                  <div className="flex-1 overflow-auto">
                    <pre className="p-6 text-sm leading-relaxed">
                      <code className="font-mono text-gray-800">
                        {mockCode}
                      </code>
                    </pre>
                  </div>

                  {/* File Footer */}
                  <div className="px-6 py-3 border-t bg-gray-50 text-xs text-muted-foreground flex items-center justify-between">
                    <span>Last modified 2 hours ago by You</span>
                    <span>Line 1, Column 1</span>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-muted-foreground">
                  <div className="text-center">
                    <FileCode className="h-16 w-16 mx-auto mb-4 opacity-50" />
                    <p>Select a file to view its contents</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

