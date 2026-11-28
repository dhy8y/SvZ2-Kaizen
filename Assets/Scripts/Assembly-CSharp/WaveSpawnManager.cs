using UnityEngine;
using System.Collections.Generic;

public class WaveSpawnManager
{
    private WaveManager waveManager
    {
        get { return WeakGlobalInstance<WaveManager>.Instance; }
    }

    private class Timer
    {
        private float mTimer = 0f;

        public float Value
        {
            get { return Mathf.Max(mTimer, 0f); }
        }

        public bool IsDone
        {
            get { return mTimer <= 0f; }
        }

        public void Reset()
        {
            mTimer = 0f;
        }

        public void Update()
        {
            mTimer -= Time.deltaTime;
        }

        public void IncreaseBy(float duration)
        {
            mTimer += Mathf.Max(0f, duration);
        }

        public void Set(float duration)
        {
            mTimer = Mathf.Max(0f, duration);
        }
    }

    private Timer mQueueTimer = new Timer();

    private class SpawnQueueItem
    {
        public string enemy;
        public float delay;

        public SpawnQueueItem(string _enemy, float _delay)
        {
            enemy = _enemy;
            delay = _delay;
        }
    }

    private class SpawnQueue
	{
		public Queue<SpawnQueueItem> queue = new Queue<SpawnQueueItem>();

		public Timer timer = new Timer();
	}

	private List<SpawnQueue> mSpawnQueues = new List<SpawnQueue>();

    public bool IsSpawning
    {
        get { return mSpawnQueues.Count > 0; }
    }

    public bool IsNextGroupReady
    {
        get { return mQueueTimer.IsDone; }
    }

    public WaveSpawnManager() {}

    public void Update()
    {
        mQueueTimer.Update();

        mSpawnQueues.RemoveAll(sq => sq.queue.Count == 0 && sq.timer.IsDone);

        if (mSpawnQueues.Count == 0) return;

        for (int i = 0; i < mSpawnQueues.Count; i++)
        {
            var spawnQueue = mSpawnQueues[i];

            spawnQueue.timer.Update();

            if (!spawnQueue.timer.IsDone || spawnQueue.queue.Count == 0)
                continue;

            var queueItem = spawnQueue.queue.Dequeue();

            if (queueItem.enemy != string.Empty)
            {
                WaveManager currentWaveManager = waveManager;
                CharactersManager charactersManager = WeakGlobalInstance<CharactersManager>.Instance;
                if (currentWaveManager == null)
                {
                    Debug.LogError("Unable to spawn enemy '" + queueItem.enemy + "': WaveManager is unavailable.");
                }
                else if (charactersManager == null)
                {
                    // The queued spawn cannot be registered. Reduce the expected count
                    // so a missing runtime manager does not leave the wave unfinished.
                    currentWaveManager.totalEnemies = Mathf.Max(0, currentWaveManager.totalEnemies - 1);
                    Debug.LogError("Unable to spawn enemy '" + queueItem.enemy + "': CharactersManager is unavailable.");
                }
                else
                {
                    var enemy = currentWaveManager.ConstructEnemy(queueItem.enemy);
                    if (enemy != null)
                    {
                        charactersManager.AddCharacter(enemy);
                    }
                    else
                    {
                        // Keep the wave completable if a data bundle references a missing
                        // enemy or its prefab cannot be constructed.
                        currentWaveManager.totalEnemies = Mathf.Max(0, currentWaveManager.totalEnemies - 1);
                        Debug.LogError("Unable to spawn enemy '" + queueItem.enemy + "'. Check EnemySchema and character resources.");
                    }
                }
            }

            spawnQueue.timer.Set(queueItem.delay);
        }
    }

    public void ResetQueueTimer()
    {
        mQueueTimer.Reset();
    }


	public void QueueSpawns(WaveCommandSchema command)
	{
		if (command == null)
		{
			Debug.LogWarning("Cannot queue a null wave spawn command.");
			return;
		}

		string enemy = DataBundleRecordKey.IsNullOrEmpty(command.enemy) ? string.Empty : command.enemy.Key;
		if (string.IsNullOrEmpty(enemy))
		{
			Debug.LogWarning("Skipping a Spawn command without a direct enemy reference.");
			return;
		}

		if (waveManager == null)
		{
			Debug.LogError("Cannot queue wave spawns because WaveManager is unavailable.");
			return;
		}

        if (mSpawnQueues.Count == 0 || command.simultaneous)
        {
            mSpawnQueues.Add(new SpawnQueue());
        }
        var spawnQueue = mSpawnQueues[mSpawnQueues.Count - 1];

		int count = (command.count > 1) ? command.count : 1;
		for (int i = 0; i < count; i++)
		{
			float delay = (i < count - 1) ? command.spacingSeconds : 2.0f;
			spawnQueue.queue.Enqueue(new SpawnQueueItem(enemy, delay));
		}

		mQueueTimer.Set(command.maxDelaySeconds);
	}

    public void DelaySpawn(float duration)
    {
        mQueueTimer.IncreaseBy(duration);
    }
}