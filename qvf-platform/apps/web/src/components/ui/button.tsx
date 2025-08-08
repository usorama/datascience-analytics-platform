import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg font-semibold transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-lg hover:shadow-xl hover:scale-105 hover:-translate-y-0.5 active:scale-95 glow-cyan",
        destructive:
          "bg-destructive text-destructive-foreground shadow-lg hover:shadow-xl hover:scale-105 hover:-translate-y-0.5 active:scale-95",
        outline:
          "border-2 border-primary bg-transparent text-primary shadow-lg hover:bg-primary/10 hover:shadow-xl hover:border-accent-hover hover:text-accent-hover hover:scale-105 hover:-translate-y-0.5 active:scale-95",
        secondary:
          "bg-secondary text-secondary-foreground shadow-lg hover:shadow-xl hover:bg-secondary/80 hover:scale-105 hover:-translate-y-0.5 active:scale-95",
        ghost: 
          "bg-transparent text-muted-foreground hover:bg-accent/20 hover:text-primary hover:shadow-lg hover:scale-105 active:scale-95",
        link: 
          "text-primary underline-offset-4 hover:underline hover:text-accent-hover transition-colors",
        floating:
          "bg-gradient-to-br from-primary to-accent-hover text-primary-foreground shadow-2xl hover:shadow-2xl hover:scale-110 active:scale-95 glow-cyan-large",
      },
      size: {
        default: "h-10 px-6 py-2 text-sm",
        sm: "h-8 rounded-md px-4 text-xs",
        lg: "h-12 rounded-xl px-8 text-base",
        icon: "h-10 w-10",
        floating: "h-14 w-14 rounded-full",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }