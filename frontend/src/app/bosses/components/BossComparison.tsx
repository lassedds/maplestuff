'use client';

import { useState, useEffect } from 'react';
import { Boss } from '@/types';
import { api } from '@/services/api';

// Extended boss data with HP and force requirements
interface ExtendedBoss extends Boss {
  hp?: number;
  hpDisplay?: string;
  level?: number | string;
  pdr?: number;
  force?: {
    type: 'AF' | 'SAC';
    reqAF?: number;
    maxAF?: number;
    reqSAC?: number;
    p1SAC?: number;
  };
  type?: string;
}

// Boss data from the JSX file
const BOSS_DATA: ExtendedBoss[] = [
  // Arcane River Pre
  { id: 0, name: 'Zakum', difficulty: 'Normal', reset_type: 'weekly', hp: 12600000, hpDisplay: '12.6M', level: 100, pdr: 100, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Hilla', difficulty: 'Normal', reset_type: 'weekly', hp: 500000000, hpDisplay: '500M', level: 120, pdr: 100, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Horntail', difficulty: 'Normal', reset_type: 'weekly', hp: 4180000000, hpDisplay: '4.18B', level: 130, pdr: 100, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Hilla', difficulty: 'Hard', reset_type: 'weekly', hp: 16800000000, hpDisplay: '16.8B', level: 170, pdr: 200, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Horntail', difficulty: 'Chaos', reset_type: 'weekly', hp: 40000000000, hpDisplay: '40B', level: 180, pdr: 200, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Magnus', difficulty: 'Normal', reset_type: 'weekly', hp: 14000000000, hpDisplay: '14B', level: 155, pdr: 100, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Magnus', difficulty: 'Hard', reset_type: 'weekly', hp: 120000000000, hpDisplay: '120B', level: 190, pdr: 300, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Zakum', difficulty: 'Chaos', reset_type: 'weekly', hp: 168000000000, hpDisplay: '168B', level: 180, pdr: 200, type: 'Arcane River Pre', is_active: true, party_size: 1, sort_order: 0 },
  
  // CRA
  { id: 0, name: 'Von Bon', difficulty: 'Chaos', reset_type: 'weekly', hp: 100000000000, hpDisplay: '100B', level: 190, pdr: 300, type: 'CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Pierre', difficulty: 'Chaos', reset_type: 'weekly', hp: 80000000000, hpDisplay: '80B', level: 190, pdr: 300, type: 'CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Queen', difficulty: 'Chaos', reset_type: 'weekly', hp: 140000000000, hpDisplay: '140B', level: 190, pdr: 300, type: 'CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Vellum', difficulty: 'Chaos', reset_type: 'weekly', hp: 200000000000, hpDisplay: '200B', level: 190, pdr: 300, type: 'CRA', is_active: true, party_size: 1, sort_order: 0 },
  
  // Post-CRA
  { id: 0, name: 'Princess No', difficulty: 'Normal', reset_type: 'weekly', hp: 200000000000, hpDisplay: '200B', level: 160, pdr: 200, type: 'Post-CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Pink Bean', difficulty: 'Chaos', reset_type: 'weekly', hp: 69300000000, hpDisplay: '69.3B', level: 190, pdr: 300, type: 'Post-CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Papulatus', difficulty: 'Chaos', reset_type: 'weekly', hp: 504000000000, hpDisplay: '504B', level: 190, pdr: 300, type: 'Post-CRA', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Gollux', difficulty: 'Hell', reset_type: 'weekly', hp: 770000000000, hpDisplay: '770B', level: 180, pdr: 300, type: 'Post-CRA', is_active: true, party_size: 1, sort_order: 0 },
  
  // Lomien
  { id: 0, name: 'Lotus', difficulty: 'Normal', reset_type: 'weekly', hp: 1570000000000, hpDisplay: '1.57T', level: 210, pdr: 300, type: 'Lomien', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Damien', difficulty: 'Normal', reset_type: 'weekly', hp: 1200000000000, hpDisplay: '1.2T', level: 210, pdr: 300, type: 'Lomien', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Lotus', difficulty: 'Hard', reset_type: 'weekly', hp: 37450000000000, hpDisplay: '37.45T', level: 210, pdr: 300, type: 'Lomien', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Damien', difficulty: 'Hard', reset_type: 'weekly', hp: 37200000000000, hpDisplay: '37.2T', level: 210, pdr: 300, type: 'Lomien', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Lotus', difficulty: 'Extreme', reset_type: 'weekly', hp: 1800000000000000, hpDisplay: '1.8Q', level: 285, pdr: 300, type: 'Lomien', is_active: true, party_size: 1, sort_order: 0 },
  
  // Arcane
  { id: 0, name: 'Guardian Slime', difficulty: 'Normal', reset_type: 'weekly', hp: 5000000000000, hpDisplay: '5T', level: 220, pdr: 300, force: { type: 'AF', reqAF: 0, maxAF: 0 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Guardian Slime', difficulty: 'Chaos', reset_type: 'weekly', hp: 90000000000000, hpDisplay: '90T', level: 250, pdr: 300, force: { type: 'AF', reqAF: 0, maxAF: 0 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Lucid', difficulty: 'Easy', reset_type: 'weekly', hp: 6000000000000, hpDisplay: '6T', level: 230, pdr: 300, force: { type: 'AF', reqAF: 360, maxAF: 540 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Lucid', difficulty: 'Normal', reset_type: 'weekly', hp: 24000000000000, hpDisplay: '24T', level: 230, pdr: 300, force: { type: 'AF', reqAF: 360, maxAF: 540 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Lucid', difficulty: 'Hard', reset_type: 'weekly', hp: 117600000000000, hpDisplay: '117.6T', level: 230, pdr: 300, force: { type: 'AF', reqAF: 360, maxAF: 540 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Will', difficulty: 'Easy', reset_type: 'weekly', hp: 12600000000000, hpDisplay: '12.6T', level: 235, pdr: 300, force: { type: 'AF', reqAF: 560, maxAF: 840 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Will', difficulty: 'Normal', reset_type: 'weekly', hp: 25200000000000, hpDisplay: '25.2T', level: 235, pdr: 300, force: { type: 'AF', reqAF: 560, maxAF: 840 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Will', difficulty: 'Hard', reset_type: 'weekly', hp: 126000000000000, hpDisplay: '126T', level: 250, pdr: 300, force: { type: 'AF', reqAF: 760, maxAF: 1140 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Gloom', difficulty: 'Normal', reset_type: 'weekly', hp: 25500000000000, hpDisplay: '25.5T', level: 255, pdr: 300, force: { type: 'AF', reqAF: 730, maxAF: 1095 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Gloom', difficulty: 'Chaos', reset_type: 'weekly', hp: 126000000000000, hpDisplay: '126T', level: 255, pdr: 300, force: { type: 'AF', reqAF: 730, maxAF: 1095 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Darknell', difficulty: 'Normal', reset_type: 'weekly', hp: 26000000000000, hpDisplay: '26T', level: 265, pdr: 300, force: { type: 'AF', reqAF: 850, maxAF: 1275 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Darknell', difficulty: 'Hard', reset_type: 'weekly', hp: 160000000000000, hpDisplay: '160T', level: 265, pdr: 300, force: { type: 'AF', reqAF: 850, maxAF: 1275 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Verus Hilla', difficulty: 'Normal', reset_type: 'weekly', hp: 88000000000000, hpDisplay: '88T', level: 250, pdr: 300, force: { type: 'AF', reqAF: 820, maxAF: 1230 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Verus Hilla', difficulty: 'Hard', reset_type: 'weekly', hp: 176000000000000, hpDisplay: '176T', level: 250, pdr: 300, force: { type: 'AF', reqAF: 900, maxAF: 1350 }, type: 'Arcane', is_active: true, party_size: 1, sort_order: 0 },
  
  // Sacred
  { id: 0, name: 'Seren', difficulty: 'Normal', reset_type: 'weekly', hp: 207900000000000, hpDisplay: '207.9T', level: 270, pdr: 380, force: { type: 'SAC', reqSAC: 200, p1SAC: 150 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Seren', difficulty: 'Hard', reset_type: 'weekly', hp: 483500000000000, hpDisplay: '483.5T', level: 275, pdr: 380, force: { type: 'SAC', reqSAC: 200, p1SAC: 150 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Seren', difficulty: 'Extreme', reset_type: 'weekly', hp: 5770000000000000, hpDisplay: '5.77Q', level: 280, pdr: 380, force: { type: 'SAC', reqSAC: 200, p1SAC: 150 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kalos', difficulty: 'Easy', reset_type: 'weekly', hp: 357000000000000, hpDisplay: '357T', level: 270, pdr: 380, force: { type: 'SAC', reqSAC: 200 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kalos', difficulty: 'Normal', reset_type: 'weekly', hp: 1056000000000000, hpDisplay: '1.056Q', level: 275, pdr: 380, force: { type: 'SAC', reqSAC: 300, p1SAC: 250 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kalos', difficulty: 'Chaos', reset_type: 'weekly', hp: 5120000000000000, hpDisplay: '5.12Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 330 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kalos', difficulty: 'Extreme', reset_type: 'weekly', hp: 19200000000000000, hpDisplay: '19.2Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 440 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kaling', difficulty: 'Easy', reset_type: 'weekly', hp: 921000000000000, hpDisplay: '921T', level: 275, pdr: 380, force: { type: 'SAC', reqSAC: 230 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kaling', difficulty: 'Normal', reset_type: 'weekly', hp: 3926000000000000, hpDisplay: '3.93Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 330 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kaling', difficulty: 'Hard', reset_type: 'weekly', hp: 12090000000000000, hpDisplay: '12.09Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 350 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Kaling', difficulty: 'Extreme', reset_type: 'weekly', hp: 54436000000000000, hpDisplay: '54.44Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 480 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Limbo', difficulty: 'Normal', reset_type: 'weekly', hp: 6505000000000000, hpDisplay: '6.5Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 500 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Limbo', difficulty: 'Hard', reset_type: 'weekly', hp: 12470000000000000, hpDisplay: '12.47Q', level: 285, pdr: 380, force: { type: 'SAC', reqSAC: 500 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Baldrix', difficulty: 'Normal', reset_type: 'weekly', hp: 9170000000000000, hpDisplay: '9.17Q', level: 290, pdr: 380, force: { type: 'SAC', reqSAC: 700 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Baldrix', difficulty: 'Hard', reset_type: 'weekly', hp: 20330000000000000, hpDisplay: '20.33Q', level: 290, pdr: 380, force: { type: 'SAC', reqSAC: 700 }, type: 'Sacred', is_active: true, party_size: 1, sort_order: 0 },
  
  // Black Mage
  { id: 0, name: 'Black Mage', difficulty: 'Hard', reset_type: 'weekly', hp: 471000000000000, hpDisplay: '471T', level: '265-275', pdr: 300, force: { type: 'AF', reqAF: 1320, maxAF: 1980 }, type: 'Black Mage', is_active: true, party_size: 1, sort_order: 0 },
  { id: 0, name: 'Black Mage', difficulty: 'Extreme', reset_type: 'weekly', hp: 4794000000000000, hpDisplay: '4.79Q', level: '275-280', pdr: 300, force: { type: 'AF', reqAF: 1320, maxAF: 1980 }, type: 'Black Mage', is_active: true, party_size: 1, sort_order: 0 },
];

function calculateEffectiveHP(baseHP: number, fdBonus: number): number {
  const multiplier = 1 + fdBonus;
  if (multiplier <= 0) return baseHP * 20;
  return baseHP / multiplier;
}

function calculateFDBonus(boss: ExtendedBoss, yourAF: number, yourSAC: number): number {
  if (!boss.force) return 0;
  
  if (boss.force.type === 'AF') {
    const { reqAF, maxAF } = boss.force;
    if (reqAF === 0) return 0;
    
    if (yourAF < reqAF) {
      return Math.max(-1, (yourAF - reqAF) / reqAF);
    }
    
    if (yourAF >= maxAF) return 0.50;
    
    const tier130 = reqAF * 1.3;
    const tier110 = reqAF * 1.1;
    
    if (yourAF >= tier130) {
      const progress = (yourAF - tier130) / (maxAF - tier130);
      return 0.30 + (progress * 0.20);
    }
    if (yourAF >= tier110) {
      const progress = (yourAF - tier110) / (tier130 - tier110);
      return 0.10 + (progress * 0.20);
    }
    if (yourAF >= reqAF) {
      const progress = (yourAF - reqAF) / (tier110 - reqAF);
      return progress * 0.10;
    }
    return 0;
  }
  
  if (boss.force.type === 'SAC') {
    const { reqSAC } = boss.force;
    const diff = yourSAC - reqSAC;
    
    if (diff >= 50) return 0.25;
    if (diff > 0) return diff * 0.005;
    if (diff < 0) return Math.max(-1, diff * 0.01);
    return 0;
  }
  
  return 0;
}

function formatNumber(num: number): string {
  if (num >= 1e15) return (num / 1e15).toFixed(2) + 'Q';
  if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T';
  if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
  return num.toLocaleString();
}

function getTypeColor(type?: string): string {
  const colors: Record<string, string> = {
    'Arcane River Pre': '#6b7280',
    'CRA': '#ef4444',
    'Post-CRA': '#f97316',
    'Lomien': '#eab308',
    'Arcane': '#22c55e',
    'Sacred': '#8b5cf6',
    'Black Mage': '#ec4899'
  };
  return colors[type || ''] || '#6b7280';
}

export default function BossComparison() {
  const [selectedBoss1, setSelectedBoss1] = useState<string>('');
  const [selectedBoss2, setSelectedBoss2] = useState<string>('');
  const [showEffectiveHP, setShowEffectiveHP] = useState(true);
  const [yourAF, setYourAF] = useState(1350);
  const [yourSAC, setYourSAC] = useState(180);
  const [allBosses, setAllBosses] = useState<ExtendedBoss[]>(BOSS_DATA);

  useEffect(() => {
    // Try to merge with API bosses if available
    api.getBosses(undefined, false).then(response => {
      // Merge API bosses with static data
      const merged = BOSS_DATA.map(staticBoss => {
        const apiBoss = response.bosses.find(b => 
          b.name === staticBoss.name && b.difficulty === staticBoss.difficulty
        );
        if (apiBoss) {
          return { ...staticBoss, id: apiBoss.id, crystal_meso: apiBoss.crystal_meso };
        }
        return staticBoss;
      });
      setAllBosses(merged);
    }).catch(() => {
      setAllBosses(BOSS_DATA);
    });
  }, []);

  const sortedBosses = [...allBosses].sort((a, b) => {
    const aHP = showEffectiveHP && a.hp ? calculateEffectiveHP(a.hp, calculateFDBonus(a, yourAF, yourSAC)) : (a.hp || 0);
    const bHP = showEffectiveHP && b.hp ? calculateEffectiveHP(b.hp, calculateFDBonus(b, yourAF, yourSAC)) : (b.hp || 0);
    return aHP - bHP;
  });

  const boss1 = allBosses.find(b => `${b.difficulty || ''} ${b.name}`.trim() === selectedBoss1);
  const boss2 = allBosses.find(b => `${b.difficulty || ''} ${b.name}`.trim() === selectedBoss2);

  // Dynamic transition comparison - use selected bosses from comparison tool
  const transitionBoss1 = boss1;
  const transitionBoss2 = boss2;
  
  const boss1EffHP = transitionBoss1 && transitionBoss1.hp ? calculateEffectiveHP(transitionBoss1.hp, calculateFDBonus(transitionBoss1, yourAF, yourSAC)) : 0;
  const boss2EffHP = transitionBoss2 && transitionBoss2.hp ? calculateEffectiveHP(transitionBoss2.hp, calculateFDBonus(transitionBoss2, yourAF, yourSAC)) : 0;
  const hpDiff = boss2EffHP - boss1EffHP;
  const hpMultiplier = boss1EffHP > 0 ? (boss2EffHP / boss1EffHP).toFixed(2) : '0';

  const boss1FD = transitionBoss1 ? calculateFDBonus(transitionBoss1, yourAF, yourSAC) : 0;
  const boss2FD = transitionBoss2 ? calculateFDBonus(transitionBoss2, yourAF, yourSAC) : 0;

  // Check if this is a significant transition (AF to SAC, or major difficulty jump)
  const isSignificantTransition = transitionBoss1 && transitionBoss2 && (
    (transitionBoss1.force?.type === 'AF' && transitionBoss2.force?.type === 'SAC') ||
    (boss2EffHP > 0 && boss1EffHP > 0 && (boss2EffHP / boss1EffHP) > 1.5)
  );

  return (
    <div className="space-y-6">
      {/* Dynamic Transition Alert */}
      {transitionBoss1 && transitionBoss2 && isSignificantTransition && (
        <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 rounded-lg p-6 border border-purple-700/50 relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500" />
          
          <div className="flex items-center gap-3 mb-4">
            <span className="bg-gradient-to-r from-purple-600 to-pink-600 px-3 py-1 rounded-lg text-xs font-semibold">
              ⚠️ KEY TRANSITION
            </span>
            <h3 className="text-lg font-bold text-purple-300">
              {transitionBoss1.name} {transitionBoss1.difficulty} → {transitionBoss2.name} {transitionBoss2.difficulty}
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
              <div className="text-green-400 text-sm mb-1">{transitionBoss1.name} {transitionBoss1.difficulty}</div>
              <div className="text-2xl font-bold text-green-400">
                {showEffectiveHP ? formatNumber(boss1EffHP) : transitionBoss1.hpDisplay || 'N/A'} HP
              </div>
              {showEffectiveHP && (
                <div className="text-xs text-gray-400 mt-2">
                  {boss1FD > 0 ? `+${(boss1FD * 100).toFixed(0)}% FD bonus` : boss1FD < 0 ? `${(boss1FD * 100).toFixed(0)}% FD penalty` : 'No FD bonus'}
                  <br />
                  <span className="text-gray-500">(Base: {transitionBoss1.hpDisplay || 'N/A'})</span>
                </div>
              )}
              <div className="text-green-300 text-xs mt-2">
                {transitionBoss1.force?.type === 'AF' && `Arcane Force: ${transitionBoss1.force.reqAF || 0} AF req`}
                {transitionBoss1.force?.type === 'SAC' && `Sacred Force: ${transitionBoss1.force.reqSAC || 0} SAC req`}
                {!transitionBoss1.force && 'No force requirement'}
                <br />
                PDR: {transitionBoss1.pdr || 'N/A'}%
              </div>
            </div>
            
            <div className="flex flex-col items-center justify-center text-gray-400">
              <div className="text-3xl mb-2">→</div>
              <div className={`text-lg font-bold ${showEffectiveHP && boss2EffHP > 0 && boss1EffHP > 0 && (boss2EffHP / boss1EffHP) > 1.5 ? 'text-red-400' : 'text-yellow-400'}`}>
                {showEffectiveHP && boss2EffHP > 0 && boss1EffHP > 0
                  ? `${((boss2EffHP / boss1EffHP - 1) * 100).toFixed(0)}% harder`
                  : boss2EffHP > 0 && boss1EffHP > 0
                  ? `${((boss2EffHP / boss1EffHP - 1) * 100).toFixed(0)}% HP increase`
                  : 'Compare'
                }
              </div>
              {showEffectiveHP && boss2EffHP > 0 && boss1EffHP > 0 && (
                <div className="text-xs text-red-400 mt-1">
                  {(boss2EffHP / boss1EffHP).toFixed(1)}x effective HP!
                </div>
              )}
            </div>
            
            <div className="bg-purple-900/20 border border-purple-700/50 rounded-lg p-4">
              <div className="text-purple-300 text-sm mb-1">{transitionBoss2.name} {transitionBoss2.difficulty}</div>
              <div className="text-2xl font-bold text-purple-400">
                {showEffectiveHP ? formatNumber(boss2EffHP) : transitionBoss2.hpDisplay || 'N/A'} HP
              </div>
              {showEffectiveHP && (
                <div className="text-xs text-gray-400 mt-2">
                  {boss2FD < 0 
                    ? `${(boss2FD * 100).toFixed(0)}% FD PENALTY!` 
                    : boss2FD > 0 
                      ? `+${(boss2FD * 100).toFixed(0)}% FD bonus`
                      : 'No FD bonus'
                  }
                  <br />
                  <span className="text-gray-500">(Base: {transitionBoss2.hpDisplay || 'N/A'})</span>
                </div>
              )}
              <div className="text-purple-300 text-xs mt-2">
                {transitionBoss2.force?.type === 'AF' && `Arcane Force: ${transitionBoss2.force.reqAF || 0} AF req`}
                {transitionBoss2.force?.type === 'SAC' && `Sacred Force: ${transitionBoss2.force.reqSAC || 0} SAC req`}
                {!transitionBoss2.force && 'No force requirement'}
                <br />
                PDR: {transitionBoss2.pdr || 'N/A'}% {transitionBoss2.pdr && transitionBoss1.pdr && transitionBoss2.pdr > transitionBoss1.pdr ? `(+${transitionBoss2.pdr - transitionBoss1.pdr}% more!)` : ''}
              </div>
            </div>
          </div>
          
          {(transitionBoss1.force?.type === 'AF' && transitionBoss2.force?.type === 'SAC') && (
            <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4">
              <h4 className="text-red-300 text-sm font-semibold mb-2">
                🎯 Why This Jump Feels HUGE
              </h4>
              <ul className="text-red-200 text-xs space-y-1 list-disc list-inside">
                <li><strong>Force System Change:</strong> Transitioning from Arcane Force to Sacred Force changes how FD bonuses work</li>
                <li><strong>FD Bonus Difference:</strong> AF bosses can give up to +50% FD, while SAC bosses max at +25% FD</li>
                <li><strong>FD Penalty:</strong> Being under SAC requirement means -10% FD per 10 SAC below (can stack to -100%!)</li>
                {transitionBoss2.pdr && transitionBoss1.pdr && transitionBoss2.pdr > transitionBoss1.pdr && (
                  <li><strong>PDR Jump:</strong> {transitionBoss1.pdr}% → {transitionBoss2.pdr}% means you need significantly more IED (94-95%+ visual recommended)</li>
                )}
                {transitionBoss2.force?.p1SAC && (
                  <li><strong>Phase Requirements:</strong> Phase 1 needs {transitionBoss2.force.p1SAC} SAC but Phase 2 needs {transitionBoss2.force.reqSAC} SAC - different penalties per phase</li>
                )}
                {showEffectiveHP && boss2EffHP > 0 && boss1EffHP > 0 && (
                  <li><strong>Effective HP:</strong> Due to all penalties, {transitionBoss2.name} can feel like {(boss2EffHP / boss1EffHP).toFixed(1)}x the effective HP of {transitionBoss1.name}</li>
                )}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Boss Comparison Tool */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-semibold text-white mb-4">🔍 Boss Comparison Tool</h2>
      
      {/* Stats Input */}
      <div className="bg-gray-700/50 rounded-lg p-4 mb-4 flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showEffectiveHP}
            onChange={(e) => setShowEffectiveHP(e.target.checked)}
            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded"
          />
          <span className="text-cyan-400 font-semibold text-sm">Show Effective HP</span>
        </label>
        
        {showEffectiveHP && (
          <>
            <div className="flex items-center gap-2">
              <label className="text-gray-400 text-sm">Your AF:</label>
              <input
                type="number"
                value={yourAF}
                onChange={(e) => setYourAF(parseInt(e.target.value) || 0)}
                className="w-20 bg-gray-600 border border-gray-500 rounded px-2 py-1 text-cyan-400 text-sm font-semibold"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-gray-400 text-sm">Your SAC:</label>
              <input
                type="number"
                value={yourSAC}
                onChange={(e) => setYourSAC(parseInt(e.target.value) || 0)}
                className="w-20 bg-gray-600 border border-gray-500 rounded px-2 py-1 text-purple-400 text-sm font-semibold"
              />
            </div>
          </>
        )}
      </div>

      {/* Boss Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-gray-400 text-sm mb-2">Boss 1 (From)</label>
          <select
            value={selectedBoss1}
            onChange={(e) => setSelectedBoss1(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {sortedBosses.map(boss => {
              const fullName = `${boss.difficulty || ''} ${boss.name}`.trim();
              return (
                <option key={fullName} value={fullName}>
                  {fullName} ({boss.hpDisplay || 'N/A'})
                </option>
              );
            })}
          </select>
        </div>
        
        <div>
          <label className="block text-gray-400 text-sm mb-2">Boss 2 (To)</label>
          <select
            value={selectedBoss2}
            onChange={(e) => setSelectedBoss2(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {sortedBosses.map(boss => {
              const fullName = `${boss.difficulty || ''} ${boss.name}`.trim();
              return (
                <option key={fullName} value={fullName}>
                  {fullName} ({boss.hpDisplay || 'N/A'})
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Comparison Results */}
      {boss1 && boss2 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-gray-400 text-xs mb-1">
              {showEffectiveHP ? 'Effective HP Diff' : 'HP Difference'}
            </div>
            <div className={`text-xl font-bold ${hpDiff > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {hpDiff > 0 ? '+' : ''}{formatNumber(hpDiff)}
            </div>
          </div>
          
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-gray-400 text-xs mb-1">
              {showEffectiveHP ? 'Effective Multiplier' : 'HP Multiplier'}
            </div>
            <div className="text-xl font-bold text-yellow-400">
              {hpMultiplier}x
            </div>
          </div>
          
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-gray-400 text-xs mb-1">PDR Change</div>
            <div className={`text-xl font-bold ${(boss2.pdr || 0) > (boss1.pdr || 0) ? 'text-red-400' : 'text-green-400'}`}>
              {boss1.pdr}% → {boss2.pdr}%
            </div>
          </div>
          
          {showEffectiveHP && (
            <div className="bg-gray-700/50 rounded-lg p-4 text-center">
              <div className="text-gray-400 text-xs mb-1">Your FD Bonus</div>
              <div className="text-sm font-semibold text-purple-400">
                <span className={boss1FD >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {boss1FD >= 0 ? '+' : ''}{(boss1FD * 100).toFixed(0)}%
                </span>
                {' → '}
                <span className={boss2FD >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {boss2FD >= 0 ? '+' : ''}{(boss2FD * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          )}
          
          <div className="bg-gray-700/50 rounded-lg p-4 text-center">
            <div className="text-gray-400 text-xs mb-1">Force System</div>
            <div className="text-sm font-semibold text-purple-400">
              {boss1.force?.type || 'None'} → {boss2.force?.type || 'None'}
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}
