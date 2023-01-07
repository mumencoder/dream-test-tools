
from .common import *
from . import Persist

class Pile:
    class Memory(object):
        def __init__(self, tests=None, level=0, ngram_counts=None):
            if tests is None:
                self.tests = []
            else:
                self.tests = tests
            if ngram_counts is None:
                self.ngram_counts = DreamCollider.NGram.new_accum()
            else:
                self.ngram_counts = ngram_counts
            self.level = level

        def iter_tests(self):
            yield from self.tests

        def add_test(self, tenv):
            self.tests.append( tenv )
            DreamCollider.NGram.accum_count( self.ngram_counts, tenv.attr.test.ngram_info )

        def test_count(self):
            return len(self.tests)

        def save(self):
            pass

        def load(self):
            pass

    class Filesystem(object):
        def __init__(self, metadata_file, tests_dir):
            self.metadata_file = metadata_file
            self.tests_dir = tests_dir
            self.tests = []
            self.level = 0
            self.ngram_counts = DreamCollider.NGram.new_accum()

        def iter_tests(self):
            for test_name in self.tests:
                tenv = Shared.Environment()
                tenv.attr.test.root_dir = self.tests_dir / test_name
                Persist.load_test(tenv)
                if Persist.is_generated(tenv):
                    yield tenv

        def clean(self):
            Persist.clean_tests(self.tests_dir, self.tests)

        def test_count(self):
            return len(self.tests)

        def save(self):
            pile_info = {}
            pile_info["tests_dir"] = str(self.tests_dir)
            pile_info["tests"] = self.tests
            pile_info["level"] = self.level
            pile_info["ngram_counts"] = self.ngram_counts

            with open( self.metadata_file, "w") as f:
                f.write( json.dumps( pile_info ) )

        def load(self):
            if not os.path.exists( self.metadata_file ):
                return

            with open( self.metadata_file, "r") as f:
                pile_info = json.loads( f.read() )

            self.tests_dir = Shared.Path( pile_info["tests_dir"] )
            self.tests = pile_info["tests"] 
            self.level = pile_info["level"]
            self.ngram_counts = pile_info["ngram_counts"]

class Sifter(object):
    def __init__(self, pile_size):
        self.total_tests = 0
        self.test_count_target = None

        self.pile_size = pile_size
        self.piles = set()
        self.pile_index = collections.defaultdict(set)

    def show_index(self):
        print("===")
        for i in range(0, 32):
            if len(self.pile_index[i]) == 0:
                continue
            print(f"Level: {i}, Size: {len(self.pile_index[i])}")
        print("===")

    def add_pile(self, pile):
        if pile.test_count() != self.pile_size:
            raise Exception("incorrect pile size", pile.test_count())

        self.piles.add( pile )
        self.pile_index[pile.level].add( pile )

    def iter_tests(self, env):
        for pid, pile in self.piles.items():
            for tenv in pile.iter_tests(env):
                yield tenv

    def find_smallest_merge_level(self):
        for i in range(0,32):
            piles = self.pile_index[i]
            if len(piles) < 2:
                continue
            return i
        return None

    def has_pile_at_level(self, level):
        piles = self.pile_index[level]
        return len(piles) != 0

    def find_pile(self, pile):
        piles = self.pile_index[pile.level]
        if pile in piles:
            return True
        return False

    def remove_pile(self, pile):
        piles = self.pile_index[pile.level]
        if pile not in piles or pile not in self.piles:
            raise Exception("pile not found")
        piles.remove( pile )
        self.piles.remove( pile )

    def choose_random_pile(self, merge_level):
        piles = self.pile_index[merge_level]
        return random.choice( list(piles) )

    def choose_random_piles(self, merge_level):
        piles = self.pile_index[merge_level]
        pile1 = random.choice( list(piles) )
        for i in range(0, 64):
            pile2 = random.choice( list(piles) )
            if pile1 != pile2:
                break
        if pile1 == pile2:
            raise Exception("cannot find two distinct piles")

        return (pile1, pile2)

    def merge_piles(self, pile1, pile2):
        if pile1.test_count() != pile2.test_count():
            raise Exception("test_count mismatch")
        if pile1.level != pile2.level:
            raise Exception("level mismatch")
        if not self.find_pile(pile1):
            raise Exception("pile missing")
        if not self.find_pile(pile2):
            raise Exception("pile missing")

        merge_accum = DreamCollider.NGram.new_accum()
        DreamCollider.NGram.accum_count( merge_accum, pile1.ngram_counts )
        DreamCollider.NGram.accum_count( merge_accum, pile2.ngram_counts )

        pooled_tests = []
        for tenv in pile1.iter_tests():
            score = DreamCollider.NGram.score_test( merge_accum, tenv.attr.test.ngram_info )
            pooled_tests.append( {"tenv": tenv, "score":score} )
        for tenv in pile2.iter_tests():
            score = DreamCollider.NGram.score_test( merge_accum, tenv.attr.test.ngram_info )
            pooled_tests.append( {"tenv": tenv, "score":score } )

        scores = [entry["score"] for entry in pooled_tests]

        mean = statistics.mean( scores )
        stdev = statistics.stdev( scores )
        z_idx = collections.defaultdict(list)
        for entry in pooled_tests:
            entry["z"] = int(5 * (entry["score"] - mean) / stdev)
            z_idx[ entry["z"] ].append( entry )

        passing_tests = []
        for z, entries in sorted(z_idx.items(), key=lambda e: e[0], reverse=True):
            passing_tests += entries
            if len(passing_tests) > pile1.test_count() :
                break
        passing_tests = passing_tests[:pile1.test_count() ]

        new_pile = Pile.Memory(tests=[e["tenv"] for e in passing_tests], level=pile1.level+1, ngram_counts=merge_accum)
        self.remove_pile( pile1 )
        self.remove_pile( pile2 )
        self.add_pile( new_pile )
