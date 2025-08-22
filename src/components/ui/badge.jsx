import React from 'react'

export const Badge = ({ children, className = '', variant = 'default', ...props }) => {
  const baseClasses = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium'
  
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    secondary: 'bg-gray-100 text-gray-800',
    destructive: 'bg-red-100 text-red-800',
    outline: 'border border-gray-200 text-gray-800',
    desktop: 'bg-blue-100 text-blue-800',
    notebook: 'bg-amber-100 text-amber-800',
    secondScreen: 'bg-orange-100 text-orange-800',
    phone: 'bg-green-100 text-green-800',
    audio: 'bg-purple-100 text-purple-800',
    mouse: 'bg-teal-100 text-teal-800',
    keyboard: 'bg-indigo-100 text-indigo-800'
  }
  
  return (
    <div className={`${baseClasses} ${variants[variant]} ${className}`} {...props}>
      {children}
    </div>
  )
}
