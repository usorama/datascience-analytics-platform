"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { cn } from "@/lib/utils"

interface ThemeToggleProps {
  className?: string
  size?: "sm" | "default" | "lg"
  variant?: "default" | "outline" | "ghost" | "icon"
}

export function ThemeToggle({ 
  className,
  size = "default",
  variant = "ghost"
}: ThemeToggleProps) {
  const [mounted, setMounted] = React.useState(false)
  const { theme, setTheme } = useTheme()

  // useEffect only runs on the client, so now we can safely show the UI
  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    // Return a placeholder that matches the button size to prevent layout shift
    return (
      <div 
        className={cn(
          "inline-flex items-center justify-center rounded-md font-medium transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          "disabled:pointer-events-none disabled:opacity-50",
          {
            "h-8 w-8": size === "sm",
            "h-10 w-10": size === "default", 
            "h-11 w-11": size === "lg"
          },
          className
        )}
        aria-label="Toggle theme"
      />
    )
  }

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  const buttonClasses = cn(
    "inline-flex items-center justify-center rounded-md font-medium transition-all duration-200",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
    "disabled:pointer-events-none disabled:opacity-50",
    "hover:scale-105 active:scale-95",
    {
      // Size variants
      "h-8 w-8 text-xs": size === "sm",
      "h-10 w-10 text-sm": size === "default",
      "h-11 w-11 text-base": size === "lg",
      
      // Style variants
      "bg-background hover:bg-accent hover:text-accent-foreground": variant === "default",
      "border border-input bg-background hover:bg-accent hover:text-accent-foreground": variant === "outline",
      "hover:bg-accent hover:text-accent-foreground": variant === "ghost",
      "hover:bg-accent": variant === "icon"
    },
    className
  )

  return (
    <button
      onClick={toggleTheme}
      className={buttonClasses}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
    >
      <Sun 
        className={cn(
          "transition-all duration-300 rotate-0 scale-100",
          theme === "dark" && "rotate-90 scale-0",
          {
            "h-3 w-3": size === "sm",
            "h-4 w-4": size === "default",
            "h-5 w-5": size === "lg"
          }
        )} 
      />
      <Moon 
        className={cn(
          "absolute transition-all duration-300 rotate-90 scale-0",
          theme === "dark" && "rotate-0 scale-100",
          {
            "h-3 w-3": size === "sm", 
            "h-4 w-4": size === "default",
            "h-5 w-5": size === "lg"
          }
        )} 
      />
      <span className="sr-only">Toggle theme</span>
    </button>
  )
}

// Dropdown variant for more theme options
export function ThemeToggleDropdown({
  className
}: {
  className?: string
}) {
  const [mounted, setMounted] = React.useState(false)
  const { theme, setTheme } = useTheme()

  React.useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="h-10 w-10" />
  }

  return (
    <div className={cn("relative", className)}>
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md h-10 w-10",
          "bg-background hover:bg-accent hover:text-accent-foreground",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          "transition-colors duration-200"
        )}
        aria-label="Toggle theme"
      >
        <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
        <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      </button>
    </div>
  )
}