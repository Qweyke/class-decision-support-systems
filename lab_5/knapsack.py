import heapq


class Item:
    def __init__(self, id, weight, value):
        self.id = id
        self.weight = weight
        self.value = value
        self.ratio = value / weight


class Node:
    def __init__(self, level, profit, weight, bound, items, decision=""):
        self.level = level  # Current level in the decision tree
        self.profit = profit  # Current total value in the bag
        self.weight = weight  # Current total weight in the bag
        self.bound = bound  # Upper bound of profit in this subtree
        self.items = items  # List of item IDs currently in the bag
        self.decision = decision  # "Take" or "Skip"

    # We use a max-priority queue based on the bound
    def __lt__(self, other):
        return self.bound > other.bound


def calculate_profit_bound(node, n, W, items):
    """
    Calculates the upper bound of profit using Fractional Knapsack logic.
    This is the 'optimistic forecast' for pruning.
    """

    # Can't get more items
    if node.weight >= W:
        return 0

    # Current profit and weight
    profit_bound = node.profit
    total_weight = node.weight

    # Add items greedily as long as they fit
    j = node.level + 1
    while j < n and total_weight + items[j].weight <= W:
        total_weight += items[j].weight
        profit_bound += items[j].value
        j += 1

    # If there is still space, add the fractional part of the next item
    if j < n:
        profit_bound += (W - total_weight) * items[j].ratio

    return profit_bound


# Best-First Search in State-Space Tree
def solve_knapsack_verbose(W, weights, profits):
    n = len(weights)
    # 1. Create items and sort them by value/weight ratio (descending)
    items = sorted(
        [Item(i + 1, weights[i], profits[i]) for i in range(n)],
        key=lambda x: x.ratio,
        reverse=True,
    )

    # 2. Initialize the priority queue and variables
    queue = []
    max_p = 0
    best_items = []

    # 3. Create root node - no decision yet made
    root_b = calculate_profit_bound(Node(-1, 0, 0, 0, []), n, W, items)
    heapq.heappush(queue, Node(-1, 0, 0, root_b, [], "ROOT"))

    iteration = 0
    print(f"START: W_limit={W}, Items={n}\n")

    # 4. Process the tree
    while queue:
        curr = heapq.heappop(queue)
        iteration += 1
        indent = "  " * (curr.level + 1)

        print(
            f"[{iteration}] MAX_P: {max_p} | Node {curr.decision} (Lvl {curr.level}): P={curr.profit}, W={curr.weight}, Bound={round(curr.bound, 2)}"
        )

        # Only explore if the bound is better than current max_profit
        if curr.bound <= max_p:
            print(f"{indent}└── STATUS: PRUNED (Bound not better than current Max_P)")
            continue

        print(f"{indent}└── STATUS: ACTIVE (Exploring branches)")

        if curr.level < n - 1:
            lvl = curr.level + 1
            item = items[lvl]

            # Option A: Take the next item
            tw, tp = curr.weight + item.weight, curr.profit + item.value
            if tw <= W:
                if tp > max_p:
                    max_p = tp
                    best_items = curr.items + [item.id]
                    print(f"{indent}    ├── TAKE Item {item.id}: NEW RECORD! P={max_p}")
                else:
                    print(f"{indent}    ├── TAKE Item {item.id}: P={tp}, W={tw}")

                tb = calculate_profit_bound(Node(lvl, tp, tw, 0, []), n, W, items)
                if tb > max_p:
                    heapq.heappush(
                        queue,
                        Node(
                            lvl, tp, tw, tb, curr.items + [item.id], f"Take_{item.id}"
                        ),
                    )
            else:
                print(f"{indent}    ├── TAKE Item {item.id}: OVERWEIGHT ({tw} > {W})")

            # Option B: Do NOT take the next item
            sb = calculate_profit_bound(
                Node(lvl, curr.profit, curr.weight, 0, []), n, W, items
            )
            if sb > max_p:
                print(
                    f"{indent}    └── SKIP Item {item.id}: Bound={round(sb, 2)} (Added to Queue)"
                )
                heapq.heappush(
                    queue,
                    Node(
                        lvl, curr.profit, curr.weight, sb, curr.items, f"Skip_{item.id}"
                    ),
                )
            else:
                print(
                    f"{indent}    └── SKIP Item {item.id}: PRUNED (Bound {round(sb, 2)} <= {max_p})"
                )

    return max_p, best_items


W_limit = 15
w_vals = [2, 3, 5, 7, 1, 4, 1]
p_vals = [10, 5, 15, 7, 6, 18, 3]

final_p, selected = solve_knapsack_verbose(W_limit, w_vals, p_vals)
print(f"\nFINAL RESULT: Profit={final_p}, Selected={selected}")
