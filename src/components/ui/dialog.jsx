import React, { useState } from 'react'

export const Dialog = ({ children, open, onOpenChange }) => {
  return (
    <>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={() => onOpenChange(false)} />
          <div className="relative z-50 bg-white rounded-lg shadow-lg max-w-lg w-full mx-4">
            {children}
          </div>
        </div>
      )}
    </>
  )
}

export const DialogTrigger = ({ children, asChild, onClick }) => {
  return (
    <div onClick={onClick}>
      {children}
    </div>
  )
}

export const DialogContent = ({ children, className = '' }) => {
  return (
    <div className={`p-6 ${className}`}>
      {children}
    </div>
  )
}

export const DialogHeader = ({ children, className = '' }) => {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  )
}

export const DialogTitle = ({ children, className = '' }) => {
  return (
    <h2 className={`text-lg font-semibold ${className}`}>
      {children}
    </h2>
  )
}
