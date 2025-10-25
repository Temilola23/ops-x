"use client";

import { useEffect, useState } from "react";
import { Sparkles, Code, Zap } from "lucide-react";

const buildingSteps = [
  {
    icon: Sparkles,
    text: "Understanding your vision",
    color: "text-purple-500",
  },
  { icon: Code, text: "Generating components", color: "text-blue-500" },
  { icon: Zap, text: "Crafting beautiful UI", color: "text-yellow-500" },
  { icon: Sparkles, text: "Finalizing your app", color: "text-green-500" },
];

export function BuildingLoader() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % buildingSteps.length);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const CurrentIcon = buildingSteps[currentStep].icon;

  return (
    <div className="absolute inset-0 bg-background/95 backdrop-blur-md flex items-center justify-center z-50 w-full h-full">
      {/* Animated Background Gradient */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px]">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-green-500/20 rounded-full blur-3xl animate-pulse" />
          <div
            className="absolute inset-0 bg-gradient-to-l from-yellow-500/20 via-pink-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"
            style={{ animationDelay: "1s" }}
          />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 text-center space-y-8 max-w-md px-4">
        {/* Animated Icon */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-full blur-2xl animate-pulse" />
          </div>
          <div className="relative flex items-center justify-center">
            <CurrentIcon
              className={`w-16 h-16 ${buildingSteps[currentStep].color} animate-float`}
              strokeWidth={1.5}
            />
          </div>
        </div>

        {/* Text */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 bg-clip-text text-transparent animate-gradient">
            Building Your MVP
          </h2>

          <div className="h-8 flex items-center justify-center">
            <p
              key={currentStep}
              className={`text-lg ${buildingSteps[currentStep].color} font-medium animate-fade-in`}
            >
              {buildingSteps[currentStep].text}
            </p>
          </div>

          {/* Progress Dots */}
          <div className="flex items-center justify-center gap-2 pt-4">
            {buildingSteps.map((_, index) => (
              <div
                key={index}
                className={`h-2 rounded-full transition-all duration-500 ${
                  index === currentStep
                    ? "w-8 bg-gradient-to-r from-purple-500 to-blue-500"
                    : "w-2 bg-muted"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Code Lines Animation */}
        <div className="space-y-2 text-left font-mono text-xs text-muted-foreground/60">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-2 animate-slide-in"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="w-4 h-4 rounded-sm bg-gradient-to-br from-purple-500/20 to-blue-500/20" />
              <div className="h-2 rounded-full bg-gradient-to-r from-muted to-transparent flex-1" />
            </div>
          ))}
        </div>

        {/* Footer Text */}
        <p className="text-sm text-muted-foreground animate-pulse">
          Powered by v0.dev × Google Gemini
        </p>
      </div>

      <style jsx>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-in {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        @keyframes gradient {
          0%,
          100% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }

        .animate-fade-in {
          animation: fade-in 0.5s ease-out forwards;
        }

        .animate-slide-in {
          animation: slide-in 0.5s ease-out forwards;
          opacity: 0;
        }

        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
      `}</style>
    </div>
  );
}
