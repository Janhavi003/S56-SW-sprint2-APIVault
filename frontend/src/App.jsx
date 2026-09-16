import { useState } from 'react'
import Header from './components/Header'
import ProductSelector from './components/ProductSelector'
import VersionSelector from './components/VersionSelector'
import QuestionInput from './components/QuestionInput'
import ExampleQuestions from './components/ExampleQuestions'
import Sidebar from './components/Sidebar'
import './App.css'
function App(){const[product,setProduct]=useState('');const[version,setVersion]=useState('');const[question,setQuestion]=useState('');const[error,setError]=useState('');const ask=()=>{if(!product||!version||!question.trim()){setError('Select a product, version, and enter a question.');return}setError('');console.log({product,version,question})};const example=(q,p,v)=>{setQuestion(q);setProduct(p);setVersion(v);setError('')};return <div className="app-shell"><Header/><div className="page-layout"><main className="main-content"><div className="hero"><div className="badge-row"><span><span className="dot"/> Version-aware</span><span>Source-grounded</span><span>Developer-first</span></div><h1>Version-Aware Technical<br/>Documentation Assistant</h1><p>Select a product and version. Ask a technical question. Get a grounded answer with the exact documentation source — every time.</p></div><section className="question-card"><div className="selectors"><ProductSelector product={product} onProductChange={setProduct}/><VersionSelector version={version} onVersionChange={setVersion}/></div><QuestionInput question={question} onQuestionChange={setQuestion}/><div className="submit-row"><button className="ask-button" onClick={ask}>⌕ Ask Question</button></div>{error&&<div className="form-error">{error}</div>}</section><ExampleQuestions onSelect={example}/></main><Sidebar/></div></div>}
export default App
