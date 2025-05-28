import React from 'react';
import { Github, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          {/* Left side */}
          <div className="flex flex-col items-center md:items-start">
            <h3 className="text-lg font-semibold text-gray-900">MediaScope</h3>
            <p className="text-sm text-gray-600 mt-1">
              Новостная аналитика с использованием spaCy NLP
            </p>
          </div>

          {/* Center */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>Сделано с</span>
            <Heart className="w-4 h-4 text-red-500 fill-current" />
            <span>для дипломного проекта</span>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/RuSick/WebScraper"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm">GitHub</span>
            </a>
            
            <div className="text-sm text-gray-500">
              © 2025 MediaScope
            </div>
          </div>
        </div>

        {/* Tech stack */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex flex-wrap justify-center gap-4 text-xs text-gray-500">
            <span>Django 4.2</span>
            <span>•</span>
            <span>React 18</span>
            <span>•</span>
            <span>TypeScript</span>
            <span>•</span>
            <span>Tailwind CSS</span>
            <span>•</span>
            <span>spaCy NLP</span>
            <span>•</span>
            <span>PostgreSQL</span>
            <span>•</span>
            <span>Redis</span>
            <span>•</span>
            <span>Celery</span>
          </div>
        </div>
      </div>
    </footer>
  );
}; 