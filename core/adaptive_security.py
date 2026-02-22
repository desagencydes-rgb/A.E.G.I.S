"""
Adaptive Security Systems for AEGIS HAT Mode
Evolutionary fuzzing and pattern learning
"""

import random
import hashlib
from typing import List, Dict, Any, Set, Tuple, Callable
from dataclasses import dataclass
from loguru import logger
import json


@dataclass
class FuzzTestCase:
    """Represents a fuzzing test case"""
    payload: str
    fitness_score: float = 0.0
    generation: int = 0
    triggered_behavior: str = ""
    parent_id: Optional[str] = None
    
    @property
    def id(self) -> str:
        """Generate unique ID for test case"""
        return hashlib.md5(self.payload.encode()).hexdigest()[:8]


class EvolutionaryFuzzer:
    """
    Genetic algorithm-based fuzzer that evolves test cases
    
    This creates "stronger than known" algorithms by:
    - Learning which mutations are most effective
    - Combining successful patterns
    - Adapting to application responses
    """
    
    def __init__(
        self,
        population_size: int = 50,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.5,
        elite_size: int = 5
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = elite_size
        
        self.population: List[FuzzTestCase] = []
        self.generation = 0
        self.best_cases: List[FuzzTestCase] = []
        
        # Mutation strategies that have proven effective
        self.effective_mutations: Dict[str, int] = {}
        
        logger.info(f"Evolutionary Fuzzer initialized (pop={population_size})")
    
    def initialize_population(self, seed_payloads: List[str]):
        """Initialize population with seed payloads"""
        self.population = [
            FuzzTestCase(payload=p, generation=0)
            for p in seed_payloads[:self.population_size]
        ]
        
        # Fill remaining with mutations
        while len(self.population) < self.population_size:
            seed = random.choice(seed_payloads)
            mutated = self._mutate(seed)
            self.population.append(FuzzTestCase(payload=mutated, generation=0))
        
        logger.info(f"Population initialized with {len(self.population)} test cases")
    
    def evaluate_fitness(
        self,
        test_case: FuzzTestCase,
        test_function: Callable[[str], Tuple[bool, str]]
    ) -> float:
        """
        Evaluate fitness of a test case
        
        Args:
            test_case: Test case to evaluate
            test_function: Function that tests the payload
                          Returns (interesting, behavior_description)
        
        Returns:
            Fitness score (higher is better)
        """
        try:
            interesting, behavior = test_function(test_case.payload)
            test_case.triggered_behavior = behavior
            
            # Fitness scoring
            score = 0.0
            
            if interesting:
                score += 100.0  # Found something interesting
            
            # Reward for triggering errors
            error_keywords = ["error", "exception", "traceback", "fail", "crash"]
            score += sum(10 for kw in error_keywords if kw in behavior.lower())
            
            # Reward for unusual responses
            if len(behavior) > 100:
                score += 20
            
            # Reward for payload complexity (but not too much)
            complexity = len(set(test_case.payload)) / max(len(test_case.payload), 1)
            score += complexity * 10
            
            test_case.fitness_score = score
            return score
        
        except Exception as e:
            logger.debug(f"Fitness evaluation error: {e}")
            return 0.0
    
    def _mutate(self, payload: str) -> str:
        """
        Mutate a payload using various strategies
        
        Returns mutated payload
        """
        mutation_strategies = [
            self._mutate_insert_random,
            self._mutate_delete_random,
            self._mutate_duplicate_segment,
            self._mutate_replace_char,
            self._mutate_insert_special,
            self._mutate_case_flip,
            self._mutate_encoding,
            self._mutate_sql_injection,
            self._mutate_xss,
            self._mutate_command_injection
        ]
        
        # Choose mutation strategy (bias toward effective ones)
        if self.effective_mutations:
            # Weighted selection based on past success
            strategy = random.choices(
                mutation_strategies,
                weights=[self.effective_mutations.get(s.__name__, 1) for s in mutation_strategies]
            )[0]
        else:
            strategy = random.choice(mutation_strategies)
        
        mutated = strategy(payload)
        
        return mutated
    
    def _mutate_insert_random(self, payload: str) -> str:
        """Insert random character"""
        if not payload:
            return chr(random.randint(32, 126))
        pos = random.randint(0, len(payload))
        char = chr(random.randint(32, 126))
        return payload[:pos] + char + payload[pos:]
    
    def _mutate_delete_random(self, payload: str) -> str:
        """Delete random character"""
        if len(payload) <= 1:
            return payload
        pos = random.randint(0, len(payload) - 1)
        return payload[:pos] + payload[pos + 1:]
    
    def _mutate_duplicate_segment(self, payload: str) -> str:
        """Duplicate a segment"""
        if len(payload) < 2:
            return payload + payload
        start = random.randint(0, len(payload) - 1)
        end = random.randint(start + 1, len(payload))
        segment = payload[start:end]
        return payload + segment
    
    def _mutate_replace_char(self, payload: str) -> str:
        """Replace random character"""
        if not payload:
            return chr(random.randint(32, 126))
        pos = random.randint(0, len(payload) - 1)
        char = chr(random.randint(32, 126))
        return payload[:pos] + char + payload[pos + 1:]
    
    def _mutate_insert_special(self, payload: str) -> str:
        """Insert special characters"""
        special_chars = ["'", '"', ";", "--", "/*", "*/", "<", ">", "&", "|", "\n", "\r", "\x00"]
        pos = random.randint(0, len(payload))
        char = random.choice(special_chars)
        return payload[:pos] + char + payload[pos:]
    
    def _mutate_case_flip(self, payload: str) -> str:
        """Flip case of random character"""
        if not payload:
            return payload
        pos = random.randint(0, len(payload) - 1)
        char = payload[pos]
        new_char = char.swapcase()
        return payload[:pos] + new_char + payload[pos + 1:]
    
    def _mutate_encoding(self, payload: str) -> str:
        """Apply various encodings"""
        encodings = [
            lambda s: s.replace("'", "%27"),
            lambda s: s.replace('"', "%22"),
            lambda s: s.replace(" ", "%20"),
            lambda s: "".join(f"\\x{ord(c):02x}" for c in s[:5]) + s[5:],
            lambda s: s.encode().hex()[:len(s)*2]
        ]
        encoding = random.choice(encodings)
        try:
            return encoding(payload)
        except:
            return payload
    
    def _mutate_sql_injection(self, payload: str) -> str:
        """Insert SQL injection patterns"""
        sql_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--",
            "admin'--",
            "1' AND '1'='1"
        ]
        pattern = random.choice(sql_patterns)
        pos = random.randint(0, len(payload))
        return payload[:pos] + pattern + payload[pos:]
    
    def _mutate_xss(self, payload: str) -> str:
        """Insert XSS patterns"""
        xss_patterns = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg/onload=alert(1)>",
            "'-alert(1)-'"
        ]
        pattern = random.choice(xss_patterns)
        pos = random.randint(0, len(payload))
        return payload[:pos] + pattern + payload[pos:]
    
    def _mutate_command_injection(self, payload: str) -> str:
        """Insert command injection patterns"""
        cmd_patterns = [
            "; ls",
            "| whoami",
            "& ping -c 1 127.0.0.1",
            "`id`",
            "$(cat /etc/passwd)"
        ]
        pattern = random.choice(cmd_patterns)
        pos = random.randint(0, len(payload))
        return payload[:pos] + pattern + payload[pos:]
    
    def _crossover(self, parent1: FuzzTestCase, parent2: FuzzTestCase) -> FuzzTestCase:
        """
        Crossover two parent test cases
        
        Returns offspring test case
        """
        # Single-point crossover
        if len(parent1.payload) > 1 and len(parent2.payload) > 1:
            point1 = random.randint(0, len(parent1.payload) - 1)
            point2 = random.randint(0, len(parent2.payload) - 1)
            
            offspring_payload = parent1.payload[:point1] + parent2.payload[point2:]
        else:
            offspring_payload = parent1.payload + parent2.payload
        
        return FuzzTestCase(
            payload=offspring_payload,
            generation=self.generation,
            parent_id=f"{parent1.id}x{parent2.id}"
        )
    
    def evolve_generation(self, test_function: Callable[[str], Tuple[bool, str]]):
        """
        Evolve one generation
        
        Args:
            test_function: Function to test payloads
        """
        self.generation += 1
        
        # Evaluate fitness for all
        for test_case in self.population:
            if test_case.fitness_score == 0.0:
                self.evaluate_fitness(test_case, test_function)
        
        # Sort by fitness
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)
        
        # Keep track of best cases
        self.best_cases.extend(self.population[:3])
        self.best_cases.sort(key=lambda x: x.fitness_score, reverse=True)
        self.best_cases = self.best_cases[:20]  # Keep top 20 overall
        
        # Selection (elitism + roulette wheel)
        new_population = []
        
        # Elitism: Keep best performers
        elite = self.population[:self.elite_size]
        new_population.extend(elite)
        
        # Breed new generation
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_select()
            parent2 = self._tournament_select()
            
            # Crossover
            if random.random() < self.crossover_rate:
                offspring = self._crossover(parent1, parent2)
            else:
                offspring = FuzzTestCase(
                    payload=parent1.payload,
                    generation=self.generation
                )
            
            # Mutation
            if random.random() < self.mutation_rate:
                offspring.payload = self._mutate(offspring.payload)
            
            new_population.append(offspring)
        
        self.population = new_population
        
        logger.info(
            f"Generation {self.generation}: "
            f"Best fitness = {self.population[0].fitness_score:.2f}"
        )
    
    def _tournament_select(self, tournament_size: int = 3) -> FuzzTestCase:
        """Select individual via tournament selection"""
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def get_best_test_cases(self, n: int = 10) -> List[FuzzTestCase]:
        """Get the n best test cases found"""
        return self.best_cases[:n]


class SecurityPatternLearner:
    """
    Learn security vulnerability patterns from findings
    
    Creates "stronger than known" detection by:
    - Extracting patterns from successful finds
    - Generating new detection heuristics
    - Storing learned patterns in memory
    """
    
    def __init__(self):
        self.learned_patterns: List[Dict[str, Any]] = []
        self.pattern_success_rate: Dict[str, int] = {}
        logger.info("Security Pattern Learner initialized")
    
    def learn_from_finding(
        self,
        code_snippet: str,
        vulnerability_type: str,
        context: str = ""
    ):
        """
        Learn pattern from a successful vulnerability find
        
        Args:
            code_snippet: The vulnerable code
            vulnerability_type: Type of vulnerability
            context: Additional context
        """
        # Extract patterns
        pattern_candidates = self._extract_patterns(code_snippet)
        
        for pattern in pattern_candidates:
            # Check if pattern is new
            if not any(p["pattern"] == pattern for p in self.learned_patterns):
                self.learned_patterns.append({
                    "pattern": pattern,
                    "type": vulnerability_type,
                    "context": context,
                    "examples": [code_snippet],
                    "confidence": 0.5  # Initial confidence
                })
                logger.info(f"Learned new pattern for {vulnerability_type}: {pattern[:50]}")
            else:
                # Increase confidence of existing pattern
                for p in self.learned_patterns:
                    if p["pattern"] == pattern:
                        p["examples"].append(code_snippet)
                        p["confidence"] = min(p["confidence"] + 0.1, 1.0)
    
    def _extract_patterns(self, code: str) -> List[str]:
        """Extract potential patterns from code"""
        patterns = []
        
        # Simple pattern extraction (can be made more sophisticated)
        # Extract function calls
        import re
        func_calls = re.findall(r'\b\w+\s*\([^)]*\)', code)
        patterns.extend(func_calls[:3])  # Top 3
        
        # Extract common constructs
        constructs = re.findall(r'\b(?:if|for|while|try)\b[^:]+:', code)
        patterns.extend(constructs[:2])
        
        return patterns
    
    def get_custom_patterns(self) -> List[Dict[str, Any]]:
        """Get learned patterns for use in scanning"""
        # Return high-confidence patterns
        return [p for p in self.learned_patterns if p["confidence"] > 0.7]
