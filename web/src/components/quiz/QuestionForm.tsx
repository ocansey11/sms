'use client';

import { useState, ChangeEvent } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';

export interface QuizQuestion {
  id?: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: string[];
  correct_answer: string;
  explanation?: string;
  points: number;
  order_number: number;
}

interface QuestionFormProps {
  question: QuizQuestion;
  onUpdate: (question: QuizQuestion) => void;
  onDelete: () => void;
  questionNumber: number;
}

export function QuestionForm({ question, onUpdate, onDelete, questionNumber }: QuestionFormProps) {
  const [localQuestion, setLocalQuestion] = useState<QuizQuestion>(question);

  const updateQuestion = (updates: Partial<QuizQuestion>) => {
    const updated = { ...localQuestion, ...updates };
    setLocalQuestion(updated);
    onUpdate(updated);
  };

  const addOption = () => {
    const currentOptions = localQuestion.options || [];
    updateQuestion({ options: [...currentOptions, ''] });
  };

  const updateOption = (index: number, value: string) => {
    const options = [...(localQuestion.options || [])];
    options[index] = value;
    updateQuestion({ options });
  };

  const removeOption = (index: number) => {
    const options = [...(localQuestion.options || [])];
    options.splice(index, 1);
    updateQuestion({ options });
  };

  const handleTypeChange = (type: 'multiple_choice' | 'true_false' | 'short_answer') => {
    let options: string[] | undefined;
    let correct_answer = '';

    if (type === 'multiple_choice') {
      options = ['', '', '', ''];
    } else if (type === 'true_false') {
      options = ['True', 'False'];
      correct_answer = 'True';
    } else {
      options = undefined;
    }

    updateQuestion({ 
      question_type: type, 
      options, 
      correct_answer: correct_answer || localQuestion.correct_answer 
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm mb-4 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Question {questionNumber}</h3>
        <button 
          onClick={onDelete}
          className="text-red-500 hover:text-red-700 p-1"
          type="button"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Question Text */}
        <div>
          <label htmlFor={`question-${questionNumber}`} className="block text-sm font-medium text-gray-700 mb-1">
            Question Text *
          </label>
          <textarea
            id={`question-${questionNumber}`}
            placeholder="Enter your question here..."
            value={localQuestion.question_text}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateQuestion({ question_text: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={3}
            required
          />
        </div>

        {/* Question Type and Points */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Question Type *</label>
            <select 
              value={localQuestion.question_type} 
              onChange={(e: ChangeEvent<HTMLSelectElement>) => handleTypeChange(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="multiple_choice">Multiple Choice</option>
              <option value="true_false">True/False</option>
              <option value="short_answer">Short Answer</option>
            </select>
          </div>
          <div>
            <label htmlFor={`points-${questionNumber}`} className="block text-sm font-medium text-gray-700 mb-1">
              Points *
            </label>
            <input
              id={`points-${questionNumber}`}
              type="number"
              min="1"
              max="10"
              value={localQuestion.points}
              onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuestion({ points: parseInt(e.target.value) || 1 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>
        </div>

        {/* Options for Multiple Choice */}
        {localQuestion.question_type === 'multiple_choice' && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">Options *</label>
              <button 
                type="button" 
                onClick={addOption}
                className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Plus className="h-4 w-4 mr-1" />
                Add Option
              </button>
            </div>
            <div className="space-y-2">
              {(localQuestion.options || []).map((option, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder={`Option ${index + 1}`}
                    value={option}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateOption(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  {(localQuestion.options?.length || 0) > 2 && (
                    <button
                      type="button"
                      onClick={() => removeOption(index)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Correct Answer */}
        <div>
          <label htmlFor={`correct-${questionNumber}`} className="block text-sm font-medium text-gray-700 mb-1">
            Correct Answer *
          </label>
          {localQuestion.question_type === 'multiple_choice' ? (
            <select 
              value={localQuestion.correct_answer} 
              onChange={(e: ChangeEvent<HTMLSelectElement>) => updateQuestion({ correct_answer: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="">Select correct answer</option>
              {(localQuestion.options || []).map((option, index) => (
                <option key={index} value={option} disabled={!option.trim()}>
                  {option || `Option ${index + 1} (empty)`}
                </option>
              ))}
            </select>
          ) : localQuestion.question_type === 'true_false' ? (
            <select 
              value={localQuestion.correct_answer} 
              onChange={(e: ChangeEvent<HTMLSelectElement>) => updateQuestion({ correct_answer: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            >
              <option value="True">True</option>
              <option value="False">False</option>
            </select>
          ) : (
            <input
              id={`correct-${questionNumber}`}
              type="text"
              placeholder="Enter the correct answer"
              value={localQuestion.correct_answer}
              onChange={(e: ChangeEvent<HTMLInputElement>) => updateQuestion({ correct_answer: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          )}
        </div>

        {/* Explanation */}
        <div>
          <label htmlFor={`explanation-${questionNumber}`} className="block text-sm font-medium text-gray-700 mb-1">
            Explanation (Optional)
          </label>
          <textarea
            id={`explanation-${questionNumber}`}
            placeholder="Explain why this is the correct answer..."
            value={localQuestion.explanation || ''}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateQuestion({ explanation: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            rows={2}
          />
        </div>
      </div>
    </div>
  );
}
