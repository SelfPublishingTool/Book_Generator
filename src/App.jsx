import React, { useState, useEffect } from 'react';
import bookData from './data/book_data.json';
import { Settings, BookOpen, Download, Image as ImageIcon, Plus, Trash, Save } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [book, setBook] = useState(bookData);
  const [view, setView] = useState('editor'); // 'editor' or 'preview'
  const [activeRecipeId, setActiveRecipeId] = useState('Recipe 1');

  // Find active recipe
  const findRecipe = (id) => {
    for (const section of book.sections) {
      if (section.content) {
        const recipe = section.content.find(c => c.type === 'recipe' && c.id === id);
        if (recipe) return recipe;
      }
    }
    return null;
  };

  const activeRecipe = findRecipe(activeRecipeId);

  const calculatePageCount = (bookData) => {
    let count = 3; // Title, Copyright, TOC
    bookData.sections.forEach(section => {
      // Chapter start (ensures odd)
      if (count % 2 === 0) count++; // blank
      count++; // Intro page
      const recipes = section.content.filter(c => c.type === 'recipe');
      count += Math.ceil(recipes.length / 2);
    });
    return count;
  };

  const updateRecipe = (id, field, value) => {
    const newBook = { ...book };
    for (const section of newBook.sections) {
      const recipeIndex = section.content.findIndex(c => c.type === 'recipe' && c.id === id);
      if (recipeIndex > -1) {
        section.content[recipeIndex] = { ...section.content[recipeIndex], [field]: value };
        break;
      }
    }
    setBook(newBook);
  };

  const generateImage = (id) => {
    // In a real app, this would call an API. 
    // Here we'll simulate it by adding a placeholder URL.
    updateRecipe(id, 'image', `https://source.unsplash.com/800x450/?food,cooking,${activeRecipe.title.split(' ').join(',')}`);
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <nav className="no-print" style={{ background: '#1e293b', padding: '10px 20px', display: 'flex', gap: '20px', borderBottom: '1px solid #334155' }}>
        <button className={`btn-${view === 'editor' ? 'primary' : 'secondary'}`} onClick={() => setView('editor')}>
          <Settings size={18} style={{ marginRight: 8 }} /> Editor
        </button>
        <button className={`btn-${view === 'preview' ? 'primary' : 'secondary'}`} onClick={() => setView('preview')}>
          <BookOpen size={18} style={{ marginRight: 8 }} /> Preview & Print
        </button>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '20px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
            Current Pages: <strong>{calculatePageCount(book)}</strong> / 95 max
          </span>
          <button className="btn-secondary" onClick={() => window.print()}>
            <Download size={18} style={{ marginRight: 8 }} /> Export PDF
          </button>
        </div>
      </nav>

      {view === 'editor' ? (
        <div className="editor-layout no-print">
          <aside className="sidebar">
            <div className="sidebar-header">
              <h3>Recipes</h3>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>101 Recipes found</p>
            </div>
            {book.sections.flatMap(s => s.content).filter(c => c.type === 'recipe').map(recipe => (
              <div 
                key={recipe.id} 
                className={`recipe-list-item ${activeRecipeId === recipe.id ? 'active' : ''}`}
                onClick={() => setActiveRecipeId(recipe.id)}
              >
                {recipe.id}: {recipe.title}
              </div>
            ))}
          </aside>

          <main className="main-editor">
            {activeRecipe ? (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 30 }}>
                  <h2>Edit {activeRecipe.id}</h2>
                  <button className="btn-primary" onClick={() => generateImage(activeRecipe.id)}>
                    <ImageIcon size={18} style={{ marginRight: 8 }} /> Generate Image
                  </button>
                </div>

                <div className="form-group">
                  <label>Title</label>
                  <input value={activeRecipe.title} onChange={(e) => updateRecipe(activeRecipe.id, 'title', e.target.value)} />
                </div>

                <div className="form-group">
                  <label>Ingredients (one per line)</label>
                  <textarea 
                    rows={8} 
                    value={activeRecipe.ingredients.join('\n')} 
                    onChange={(e) => updateRecipe(activeRecipe.id, 'ingredients', e.target.value.split('\n'))} 
                  />
                </div>

                <div className="form-group">
                  <label>Instructions (one per line)</label>
                  <textarea 
                    rows={8} 
                    value={activeRecipe.instructions.join('\n')} 
                    onChange={(e) => updateRecipe(activeRecipe.id, 'instructions', e.target.value.split('\n'))} 
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div className="form-group">
                    <label>Prep Time</label>
                    <input 
                      value={activeRecipe.metadata['Prep'] || ''} 
                      onChange={(e) => {
                        const m = { ...activeRecipe.metadata, Prep: e.target.value };
                        updateRecipe(activeRecipe.id, 'metadata', m);
                      }} 
                    />
                  </div>
                  <div className="form-group">
                    <label>Cook Time</label>
                    <input 
                      value={activeRecipe.metadata['Cook'] || ''} 
                      onChange={(e) => {
                        const m = { ...activeRecipe.metadata, Cook: e.target.value };
                        updateRecipe(activeRecipe.id, 'metadata', m);
                      }} 
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Nutrition (Calories | Protein | Carbs | Fat)</label>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <input placeholder="Cal" value={activeRecipe.nutrition['Calories']} onChange={(e) => updateRecipe(activeRecipe.id, 'nutrition', { ...activeRecipe.nutrition, Calories: e.target.value })} />
                    <input placeholder="Pro" value={activeRecipe.nutrition['Protein']} onChange={(e) => updateRecipe(activeRecipe.id, 'nutrition', { ...activeRecipe.nutrition, Protein: e.target.value })} />
                    <input placeholder="Carb" value={activeRecipe.nutrition['Carbs']} onChange={(e) => updateRecipe(activeRecipe.id, 'nutrition', { ...activeRecipe.nutrition, Carbs: e.target.value })} />
                    <input placeholder="Fat" value={activeRecipe.nutrition['Fat']} onChange={(e) => updateRecipe(activeRecipe.id, 'nutrition', { ...activeRecipe.nutrition, Fat: e.target.value })} />
                  </div>
                </div>
              </motion.div>
            ) : (
              <div style={{ textAlign: 'center', marginTop: 100, color: '#64748b' }}>
                Select a recipe to begin editing
              </div>
            )}
          </main>
        </div>
      ) : (
        <BookPreview book={book} />
      )}
    </div>
  );
}

function BookPreview({ book }) {
  let pageCounter = 1;

  // Helper to add a page and increment counter
  const Page = ({ children, isBlank = false, style = {} }) => {
    const pageNum = pageCounter++;
    return (
      <div className={`page ${isBlank ? 'blank' : ''}`} style={style}>
        {children}
        <div className="page-number">{pageNum}</div>
      </div>
    );
  };

  // Helper to ensure next section starts on an ODD page (Right side)
  const ensureOddPage = () => {
    if (pageCounter % 2 === 0) {
      return <Page isBlank={true} style={{ justifyContent: 'center', alignItems: 'center' }}>
        <p style={{ color: '#ccc', fontStyle: 'italic', fontSize: '0.8rem' }}>This page intentionally left blank</p>
      </Page>;
    }
    return null;
  };

  return (
    <div className="page-container">
      {/* 1. Title Page (Page 1 - ODD) */}
      <Page style={{ justifyContent: 'center', textAlign: 'center', background: 'linear-gradient(160deg, var(--green) 0%, var(--forest) 70%)', color: '#f4ecd6', padding: 0 }}>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ padding: '0.8in', border: '1px solid rgba(244,236,214,0.3)', background: 'rgba(0,0,0,0.05)', borderRadius: '6px', margin: '1in' }}>
          <p style={{ textTransform: 'uppercase', letterSpacing: '0.4em', fontSize: '11pt', color: '#d8c896', fontWeight: 600, marginBottom: '1em' }}>Priscilla Quinn</p>
          <div style={{ width: '60px', height: '2px', background: '#d8c896', margin: '0 auto 1.2em' }}></div>
          <h1 style={{ fontFamily: 'Cormorant Garamond', fontSize: '42pt', lineHeight: 1.05, fontWeight: 700, marginBottom: '0.6em', color: '#f4ecd6' }}>{book.title}</h1>
          <h3 style={{ fontStyle: 'italic', fontSize: '13pt', lineHeight: 1.45, color: '#e8dcb6', marginBottom: '2em' }}>{book.subtitle}</h3>
          <p style={{ fontSize: '14pt', letterSpacing: '0.2em', textTransform: 'uppercase', color: '#d8c896' }}>By <strong>Priscilla Quinn</strong></p>
        </motion.div>
      </Page>

      {/* 2. Copyright / Disclaimer (Page 2 - EVEN) */}
      <Page>
        <div style={{ fontSize: '9.5pt', lineHeight: '1.55', color: 'var(--ink-soft)', textAlign: 'justify' }}>
          <p style={{ textAlign: 'center', fontWeight: 'bold', fontSize: '10pt', marginBottom: '1.4em', color: 'var(--muted)', letterSpacing: '0.05em' }}>
            © Copyright 2026 by Priscilla Quinn - All rights reserved.
          </p>
          <hr style={{ border: 'none', borderTop: '1px solid var(--line)', margin: '1.4em auto', width: '80px' }} />
          <h4 style={{ textAlign: 'center', textTransform: 'uppercase', letterSpacing: '0.3em', fontSize: '10pt', color: 'var(--green)', fontWeight: 700, marginBottom: '1.2em' }}>Disclaimer</h4>
          <p>The following book is provided below with the aim of delivering information that is as precise and dependable as possible. However, purchasing this book implies an acknowledgment that both the publisher and the author are not experts in the discussed topics, and any recommendations or suggestions contained herein are solely for entertainment purposes. It is advised that professionals be consulted as needed before acting on any endorsed actions.</p>
          <p>This statement is considered fair and valid by both the American Bar Association and the Committee of Publishers Association, and it holds legal binding throughout the United States.</p>
          <p>Moreover, any transmission, duplication, or reproduction of this work, including specific information, will be deemed an illegal act, regardless of whether it is done electronically or in print. This includes creating secondary or tertiary copies of the work or recorded copies, which are only allowed with the express written consent from the Publisher. All additional rights are reserved.</p>
          <p>The information in the following pages is generally considered to be a truthful and accurate account of facts. As such, any negligence, use, or misuse of the information by the reader will result in actions falling solely under their responsibility. There are no scenarios in which the publisher or the original author can be held liable for any difficulties or damages that may occur after undertaking the information described herein.</p>
          <p>Additionally, the information in the following pages is intended solely for informational purposes and should be considered as such. As fitting its nature, it is presented without assurance regarding its prolonged validity or interim quality. Mention of trademarks is done without written consent and should not be construed as an endorsement from the trademark holder.</p>
        </div>
      </Page>

      {/* 3. Table of Contents (Page 3 - ODD) */}
      <Page>
        <h2 style={{ fontFamily: 'Playfair Display', fontSize: '2rem', borderBottom: '2px solid #eee', paddingBottom: '1rem' }}>Table of Contents</h2>
        <div style={{ marginTop: '2rem' }}>
          {book.sections.map((section, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
              <span style={{ fontWeight: 600 }}>{section.title.replace('# ', '')}</span>
              <span style={{ flex: 1, borderBottom: '1px dotted #ccc', margin: '0 10px', alignSelf: 'center' }}></span>
            </div>
          ))}
        </div>
      </Page>

      {/* 4. Content Sections */}
      {book.sections.map((section, sIdx) => {
        const elements = [];
        
        // Ensure Chapter starts on ODD page
        const blank = ensureOddPage();
        if (blank) elements.push(blank);

        // Chapter Intro Page
        elements.push(
          <Page key={`intro-${sIdx}`} style={{ justifyContent: 'center', background: 'linear-gradient(160deg, var(--green) 0%, var(--forest) 70%)', color: '#f4ecd6', padding: 0 }}>
            <motion.div initial={{ y: 20, opacity: 0 }} whileInView={{ y: 0, opacity: 1 }} style={{ textAlign: 'center', padding: '1in', width: '100%', borderTop: '1px solid rgba(244,236,214,0.3)', borderBottom: '1px solid rgba(244,236,214,0.3)', margin: '0.8in' }}>
              <p style={{ textTransform: 'uppercase', letterSpacing: '0.5em', fontSize: '11pt', color: '#d8c896', fontWeight: 600, marginBottom: '1em' }}>Chapter {sIdx + 1}</p>
              <h1 style={{ fontFamily: 'Cormorant Garamond', fontSize: '48pt', fontWeight: 700, lineHeight: 1.05, margin: '0 0 0.5em', color: '#f4ecd6' }}>{section.title.replace('# ', '')}</h1>
              <div style={{ width: '80px', height: '2px', background: '#d8c896', margin: '0.8em auto' }}></div>
              {section.subtitle && <p style={{ fontStyle: 'italic', fontSize: '14pt', color: '#e8dcb6' }}>{section.subtitle}</p>}
            </motion.div>
          </Page>
        );

        // Recipes (2 per page - Side by Side)
        const recipes = section.content.filter(c => c.type === 'recipe');
        groupInPairs(recipes).forEach((pair, pIdx) => {
          elements.push(
            <Page key={`recipes-${sIdx}-${pIdx}`}>
              <div className="recipe-page">
                {pair.map(recipe => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>
            </Page>
          );
        });

        return elements;
      })}
    </div>
  );
}

function RecipeCard({ recipe }) {
  return (
    <div className="recipe-card">
      <div>
        <div className="recipe-header">
          <h2 className="recipe-title">{recipe.title}</h2>
          <span className="recipe-id">{recipe.id}</span>
        </div>

        <div className="badge-container">
          <div className="badge badge-protein">
            {recipe.metadata['Protein Source'] || 'High Protein'}
          </div>
          <div className="badge badge-time">
            Prep: {recipe.metadata['Prep']} | Cook: {recipe.metadata['Cook']}
          </div>
          <div className="badge badge-yield">
            {recipe.metadata['Yield']}
          </div>
        </div>

        {recipe.image ? (
          <img className="recipe-image" src={recipe.image} alt={recipe.title} />
        ) : (
          <div className="recipe-image" style={{ background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', color: '#94a3b8' }}>
            No Image Generated
          </div>
        )}

        <div className="recipe-content">
          <div>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--book-primary)' }}>Ingredients</h4>
            <ul className="ingredients-list">
              {recipe.ingredients.map((ing, idx) => (
                <li key={idx}>{ing}</li>
              ))}
            </ul>
          </div>
          <div>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--book-primary)' }}>Instructions</h4>
            <ol className="instructions-list">
              {recipe.instructions.map((ins, idx) => (
                <li key={idx}>{ins}</li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <div className="nutrition-box">
          <div className="nutrition-item">
            <span className="nutrition-value">{recipe.nutrition['Calories']}</span>
            <span className="nutrition-label">Cal</span>
          </div>
          <div className="nutrition-item">
            <span className="nutrition-value">{recipe.nutrition['Protein']}</span>
            <span className="nutrition-label">Pro</span>
          </div>
          <div className="nutrition-item">
            <span className="nutrition-value">{recipe.nutrition['Carbs']}</span>
            <span className="nutrition-label">Carb</span>
          </div>
          <div className="nutrition-item">
            <span className="nutrition-value">{recipe.nutrition['Fat']}</span>
            <span className="nutrition-label">Fat</span>
          </div>
        </div>
        {recipe.notes && (
          <p className="recipe-notes">
            <strong>Note:</strong> {recipe.notes}
          </p>
        )}
      </div>
    </div>
  );
}

function groupInPairs(arr) {
  const res = [];
  for (let i = 0; i < arr.length; i += 2) {
    res.push(arr.slice(i, i + 2));
  }
  return res;
}

export default App;
