
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

/*
  Eco-Modern Button System
  Using theme CSS variables from globals.css:
  - --accent (Lime Green) for primary actions
  - --secondary (Gray) for cancel/close
  - --destructive (Rose) for delete actions
*/

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-bold ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        /*
          PRIMARY (Lime/Accent) - Main action buttons (Add, Create, Save)
          Uses --accent CSS variable (Lime Green)
        */
        default: "bg-accent text-accent-foreground hover:bg-[hsl(var(--accent-hover))] shadow-lg shadow-accent/25 hover:shadow-xl hover:shadow-accent/30",

        /*
          SECONDARY - Cancel, Close, secondary actions
          Uses --secondary CSS variable
        */
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 hover:text-secondary-foreground",

        /*
          OUTLINE - Bordered buttons for tertiary actions
        */
        outline:
          "border-2 border-input bg-background hover:bg-accent/10 hover:text-accent",

        /*
          GHOST - Minimal buttons for card actions
        */
        ghost: "hover:bg-muted text-foreground",

        /*
          DESTRUCTIVE - Delete, Remove actions
          Uses --destructive CSS variable
        */
        destructive:
          "bg-destructive/10 text-destructive hover:bg-destructive/20",

        /*
          LINK - Text-only buttons
        */
        link: "text-accent underline-offset-4 hover:underline",
      },
      size: {
        default: "h-11 px-6 py-3",
        sm: "h-9 px-4 py-2 text-xs",
        lg: "h-12 px-8 py-4 text-base",
        icon: "h-11 w-11",
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
